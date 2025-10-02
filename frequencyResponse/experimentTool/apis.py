from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple
import numpy as np
import control as ct

try:
    from scipy import optimize as opt
except Exception:
    opt = None

from .design import ModelSpec
from .core import build_rational_tf, bode_arrays
from .io import read_csv
from .utils import info

def _movavg(x, k):
    k = max(3, int(k) | 1)  # odd
    pad = k // 2
    xpad = np.pad(x, (pad,pad), mode='edge')
    ker = np.ones(k) / k
    return np.convolve(xpad, ker, mode='valid')

def _linfit(x, y):
    A = np.vstack([x, np.ones_like(x)]).T
    m, b = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(m), float(b)

def fit_simple_from_csv(csv_path: str, diag: Dict) -> ModelSpec:
    D = read_csv(csv_path)
    w, mag_db, phase_deg = D["w"], D["mag_db"], D["phase_deg"]
    logw = np.log10(w)
    n_low = max(60, int(0.15*len(w)))
    m_low, b_low = _linfit(logw[:n_low], mag_db[:n_low])
    lam_slope = int(np.clip(round(-m_low/20.0), 0, 2))
    phase_low = float(np.median(phase_deg[:n_low]))
    lam_phase = int(np.clip(round(-phase_low/90.0), 0, 2))
    lam = lam_slope if lam_slope == lam_phase else lam_slope
    K_est = 10**(b_low/20.0)

    dmag = np.gradient(_movavg(mag_db, 7), logw)
    thr1 = float(np.nanmedian(dmag[:10]) - 10.0)
    try:    i1 = int(np.where(dmag < thr1)[0][0])
    except: i1 = int(len(w)*0.2)
    w1 = float(w[i1])

    try:    i2 = int(np.where(dmag < -30.0)[0][0])
    except: i2 = int(len(w)*0.6)
    w2 = float(w[i2])

    zeta_est = 0.7
    win = (w > 0.6*w2) & (w < 1.4*w2)
    Mr_db = 0.0; w_peak = None
    if np.any(win):
        idxp = np.argmax(mag_db[win]); w_peak = float(w[win][idxp])
        Mr_db = float(mag_db[win][idxp] - np.interp(w_peak, w, _movavg(mag_db, 11)))
        Mr = 10**(max(0.0, Mr_db)/20.0)
        if Mr > 1.01:
            zs = np.linspace(0.05, 0.8, 500)
            M = 1.0/(2.0*zs*np.sqrt(1.0 - zs*zs))
            zeta_est = float(zs[np.argmin(np.abs(M - Mr))])

    ph = np.unwrap(np.radians(phase_deg))
    n_hi = max(8, int(0.25*len(w)))
    m_hi, _ = _linfit(w[-n_hi:], ph[-n_hi:])
    T_est = float(max(0.0, -m_hi))

    zeros = [2.0]
    mid = (w > 1.2*w1) & (w < 0.8*w2)
    if np.any(mid):
        m_mid, _ = _linfit(np.log10(w[mid]), mag_db[mid])
        if m_mid < -10:
            zeros = []

    diag.update({
        "mode": "fit",
        "lowfreq_n": n_low,
        "slope_low_db_per_dec": m_low,
        "intercept_low_db": b_low,
        "phase_low_mean_deg": float(phase_low),
        "lambda_from_slope": lam_slope,
        "lambda_from_phase": lam_phase,
        "lambda_chosen": lam,
        "K_from_intercept": K_est,
        "idx_wp": i1, "wp": w1,
        "idx_wn": i2, "wn": w2,
        "resonance_w_peak": w_peak, "Mr_db": Mr_db,
        "zeta_est": zeta_est,
        "n_high_for_delay": n_hi,
        "delay_est_T": T_est
    })

    info(f"λ candidates: slope→{lam_slope}, phase→{lam_phase} → chosen {lam}")
    info(f"K estimate: {K_est:.3g}; corners ωp≈{w1:.3g}, ωn≈{w2:.3g}; ζ≈{zeta_est:.3f}; T≈{T_est:.4g} s")
    return ModelSpec(K=float(K_est), lam=int(lam), zeros=zeros,
                     poles1=[w1], wns=[w2], zetas=[zeta_est], delay=T_est)

def refine_fit(spec: ModelSpec, data: Dict[str,np.ndarray], delay_method: str,
               diag: Dict) -> ModelSpec:
    if opt is None:
        return spec
    w = data["w"]; m_t = data["mag_db"]; p_t = data["phase_deg"]
    use_zero = len(spec.zeros) > 0

    def pack(s: ModelSpec):
        return np.array([np.log(s.K),
                         np.log(s.poles1[0] if s.poles1 else 1.0),
                         np.log(s.wns[0] if s.wns else 5.0),
                         s.zetas[0] if s.zetas else 0.7,
                         s.delay], dtype=float)

    def unpack(x):
        return ModelSpec(K=float(np.exp(x[0])), lam=spec.lam,
                         zeros=(spec.zeros if use_zero else []),
                         poles1=[float(np.exp(x[1]))],
                         wns=[float(np.exp(x[2]))],
                         zetas=[float(np.clip(x[3], 0.05, 2.0))],
                         delay=float(np.clip(x[4], 0.0, 5.0)))

    x0 = pack(spec)
    lb = np.array([np.log(1e-4), np.log(1e-3), np.log(1e-3), 0.05, 0.0])
    ub = np.array([np.log(1e4),  np.log(1e3),  np.log(1e3),  2.0,  5.0])

    def residuals(x):
        s = unpack(x)
        G = build_rational_tf(s)
        sys_f = G
        if delay_method == "pade" and s.delay > 0:
            numd, dend = ct.pade(s.delay, 6)
            sys_f = G * ct.TransferFunction(numd, dend)
        bode = bode_arrays(sys_f, w, s.delay, delay_method=delay_method)
        return np.hstack([1.0*(bode.mag_db - m_t), 0.01*(bode.phase_deg - p_t)])

    res = opt.least_squares(residuals, x0, bounds=(lb, ub),
                            xtol=1e-6, ftol=1e-6, gtol=1e-6, max_nfev=200)
    sA = unpack(res.x)

    families = [("A(no-zero)", sA)]
    if not use_zero:
        with_zero = ModelSpec(K=sA.K, lam=sA.lam, zeros=[2.0], poles1=sA.poles1,
                              wns=sA.wns, zetas=sA.zetas, delay=sA.delay)
        families.append(("B(with-zero)", with_zero))

    best = None; sse_best = None; winners = {}
    for name, s in families:
        G = build_rational_tf(s)
        sys_f = G
        if delay_method == "pade" and s.delay > 0:
            numd, dend = ct.pade(s.delay, 6)
            sys_f = G * ct.TransferFunction(numd, dend)
        bode = bode_arrays(sys_f, w, s.delay, delay_method=delay_method)
        err = np.hstack([1.0*(bode.mag_db - m_t), 0.01*(bode.phase_deg - p_t)])
        sse = float(np.sum(err*err))
        winners[name] = {"spec": asdict(s), "sse": sse}
        if best is None or sse < sse_best:
            best, sse_best = s, sse

    diag["refine"] = winners
    info("Refine comparison: " + ", ".join(f"{k}={v['sse']:.3g}" for k,v in winners.items()))
    return best

# Facade
@dataclass(slots=True)
class ExperimentService:
    delay_method: str = "frd"
    pade_order: int = 6

    def bode_for(self, spec: ModelSpec, wmin: float, wmax: float, npts: int):
        G = build_rational_tf(spec)
        sys_for_freq = G
        if self.delay_method == "pade" and spec.delay > 0:
            numd, dend = ct.pade(spec.delay, self.pade_order)
            sys_for_freq = G * ct.TransferFunction(numd, dend)
        w = np.logspace(np.log10(wmin), np.log10(wmax), npts)
        return sys_for_freq, bode_arrays(sys_for_freq, w, spec.delay, delay_method=self.delay_method)

    def fit_from_csv(self, csv_path: str, *, refine: bool = False) -> tuple[ModelSpec, dict]:
        diag: Dict = {}
        spec0 = fit_simple_from_csv(csv_path, diag)
        if refine:
            data = read_csv(csv_path)
            specR = refine_fit(spec0, data, self.delay_method, diag)
            return specR, {"initial": spec0.as_dict(), "refined": specR.as_dict(), "diagnostics": diag}
        return spec0, {"initial": spec0.as_dict(), "diagnostics": diag}
