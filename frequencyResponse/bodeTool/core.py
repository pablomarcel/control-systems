from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
import math
import numpy as np
import control as ct

from .io import parse_list, parse_roots, parse_factors
from .utils import tf_arrays, pretty_tf
from .apis import Margins, ClosedLoopFR

@dataclass
class TFBuilder:
    def build_from_modes(
        self,
        num: str | None, den: str | None,
        gain: float | None, zeros: str | None, poles: str | None,
        fnum: str | None, fden: str | None, K: float
    ) -> ct.TransferFunction:
        mode_count = 0
        if num or den: mode_count += 1
        if (gain is not None) or (zeros is not None) or (poles is not None): mode_count += 1
        if fnum or fden: mode_count += 1
        if mode_count != 1:
            raise ValueError("Specify exactly ONE input mode for a TF.")
        if fnum or fden:
            n = parse_factors(fnum or "1", Kval=K)
            d = parse_factors(fden or "1", Kval=K)
            return ct.tf(n, d)
        if (gain is not None) or (zeros is not None) or (poles is not None):
            z = parse_roots(zeros)
            p = parse_roots(poles)
            n = np.poly(z) if z else np.array([1.0])
            n = float(gain if gain is not None else 1.0) * n
            d = np.poly(p) if p else np.array([1.0])
            return ct.tf(n, d)
        return ct.tf(parse_list(num or "1"), parse_list(den or "1"))

@dataclass
class FrequencyGrid:
    def break_freqs(self, G: ct.TransferFunction) -> np.ndarray:
        z = np.roots(tf_arrays(G)[0])
        p = np.roots(tf_arrays(G)[1])
        vals = []
        for s in np.concatenate([z, p]):
            if np.isfinite(s):
                w = abs(s)
                if w > 0:
                    vals.append(w)
        return np.sort(np.array(vals)) if vals else np.array([])

    def make(self, G: ct.TransferFunction, wmin: float | None, wmax: float | None, npts: int) -> np.ndarray:
        br = self.break_freqs(G)
        if wmin is None:
            wmin = max(1e-3, float(np.min(br)/10.0) if br.size else 1e-2)
        if wmax is None:
            wmax = float(np.max(br)*10.0) if br.size else 1e2
            if wmax < 10*wmin:
                wmax = 10*wmin
        return np.logspace(math.log10(wmin), math.log10(wmax), npts)

@dataclass
class Analyzer:
    def bode_data(self, sys: ct.TransferFunction, w: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        try:
            mag, phase, ww = ct.freqresp(sys, w)
            mag = np.asarray(mag).squeeze()
            phase = np.asarray(phase).squeeze()
            ww = np.asarray(ww).ravel()
            return mag, phase, ww
        except Exception:
            num, den = tf_arrays(sys)
            s = 1j*w
            H = np.polyval(num, s) / np.polyval(den, s)
            return np.abs(H), np.angle(H), w

    def _estimate_margins_from_arrays(self, w: np.ndarray, mag: np.ndarray, phase_deg: np.ndarray) -> Margins:
        wgc = float("nan"); wpc = float("nan"); pm = float("nan"); gm = float("inf")
        for k in range(len(w)-1):
            if (mag[k]-1)*(mag[k+1]-1) <= 0:
                t = (1.0 - mag[k]) / (mag[k+1]-mag[k] + 1e-16)
                wgc = float(w[k] + t*(w[k+1]-w[k]))
                ph_at_gc = float(np.interp(wgc, w, phase_deg))
                pm = 180.0 + ph_at_gc
                break
        for k in range(len(w)-1):
            if (phase_deg[k]+180.0)*(phase_deg[k+1]+180.0) <= 0:
                t = (-180.0 - phase_deg[k]) / (phase_deg[k+1]-phase_deg[k] + 1e-16)
                wpc = float(w[k] + t*(w[k+1]-w[k]))
                mag_at_pc = float(np.interp(wpc, w, mag))
                gm = (1.0/mag_at_pc) if mag_at_pc>0 else float("inf")
                break
        gm_db = 20.0*np.log10(gm) if gm>0 and np.isfinite(gm) else float("inf")
        return Margins(gm=gm, pm=pm, wgc=wgc, wpc=wpc, gm_db=gm_db)

    def compute_margins(self, L: ct.TransferFunction, w: np.ndarray) -> Margins:
        mag, phase, ww = self.bode_data(L, w)
        phase_deg = np.degrees(np.unwrap(phase))
        est = self._estimate_margins_from_arrays(ww, mag, phase_deg)
        gm, pm = est.gm, est.pm
        try:
            out = ct.margin(L)
            if isinstance(out, (list, tuple)) and len(out) >= 2:
                gm = float(out[0]) if np.isfinite(out[0]) else gm
                pm = float(out[1]) if np.isfinite(out[1]) else pm
            else:
                gm = float(getattr(out, "gm", gm))
                pm = float(getattr(out, "pm", pm))
        except Exception:
            pass
        gm_db = 20.0*np.log10(gm) if gm > 0 and np.isfinite(gm) else float("inf")
        return Margins(gm=gm, pm=pm, wgc=est.wgc, wpc=est.wpc, gm_db=gm_db)

    def closedloop_metrics(self, L: ct.TransferFunction, w: np.ndarray) -> ClosedLoopFR:
        T = ct.minreal(ct.feedback(L, 1), verbose=False)
        mag, phase, ww = self.bode_data(T, w)
        idx = int(np.argmax(mag))
        Mr = float(mag[idx]); wr = float(ww[idx])
        Mr_db = 20.0*np.log10(Mr) if Mr>0 else -np.inf
        m0 = float(mag[0]); target = m0/math.sqrt(2.0)
        wb = float("nan")
        for i in range(len(ww)-1):
            if (mag[i]-target)*(mag[i+1]-target) <= 0:
                t = (target - mag[i])/(mag[i+1]-mag[i] + 1e-16)
                wb = float(ww[i] + t*(ww[i+1]-ww[i]))
                break
        return ClosedLoopFR(wb=wb, Mr_db=Mr_db, wr=wr)

    def nyq_encirclements(self, L: ct.TransferFunction, w: np.ndarray, center=(-1.0,0.0)) -> int:
        n, d = tf_arrays(L)
        jw = 1j*w
        Ljw = np.polyval(n, jw)/np.polyval(d, jw)
        track = np.concatenate([Ljw, np.conjugate(Ljw[-2:0:-1])])
        z = track - (center[0] + 1j*center[1])
        ang = np.unwrap(np.angle(z))
        dtheta = ang[-1] - ang[0]
        return int(round(-dtheta/(2*math.pi)))
