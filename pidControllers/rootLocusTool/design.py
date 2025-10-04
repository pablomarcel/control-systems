from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import control as ct

from .utils import parse_poly, complex_arg
from .core import rlocus_map

# ---------------- Data classes ----------------
@dataclass(slots=True)
class RootLocusConfig:
    example: Optional[str] = None
    num: Optional[str] = None
    den: Optional[str] = None
    zeta_values: Optional[List[float]] = None
    zeta_range: Optional[Tuple[float, float]] = None
    zeta_n: int = 4
    omega: Tuple[float, float, int] = (0.2, 12.0, 300)
    kmin: int = -1
    kmax: int = 1
    a_override: Optional[float] = None
    ray_wmin: float = 0.0
    ray_scale: float = 1.05
    xlim: Optional[Tuple[float, float]] = None
    ylim: Optional[Tuple[float, float]] = None
    title: str = "Root Locus with ζ-rays"

@dataclass(slots=True)
class DesignPoint:
    zeta: float
    omega: float
    a: float
    K: float
    Kp: float
    Ti: float
    Td: float
    sigma: float
    jw: float

# ---------------- Core logic ----------------
def _zeta_line_points(z: float, wmin: float, wmax: float, npts: int = 200):
    wmin = max(0.0, float(wmin))
    wmax = max(wmin + 1e-9, float(wmax))
    w = np.linspace(wmin, wmax, int(npts))
    alpha = z / math.sqrt(1 - z*z)     # σ = -α ω
    sigma = -alpha*w
    return sigma, w

def _solve_a_on_ray(s: complex, gp_angle: float, s_angle: float, kmin: int=-2, kmax: int=2) -> List[float]:
    res = []
    for k in range(kmin, kmax+1):
        theta_target = 0.5 * ((2*k + 1)*math.pi - gp_angle + s_angle)
        tanv = math.tan(theta_target)
        if abs(tanv) < 1e-8:
            continue
        a = (s.imag / tanv) - s.real
        if a > 1e-8 and math.isfinite(a) and a < 1e9:
            res.append(a)
    res.sort()
    uniq = []
    for v in res:
        if not uniq or abs(v - uniq[-1]) > 1e-6:
            uniq.append(v)
    return uniq

def _gain_from_magnitude(s: complex, a: float, Gp: ct.TransferFunction):
    Gp_eval = ct.evalfr(Gp, s)
    num_over_den_Gc = (s + a)**2 / s
    K = 1.0 / abs(num_over_den_Gc * Gp_eval)
    Kp = 2*a*K
    Ti = 2.0 / a
    Td = 1.0 / (2.0*a)
    return K, Kp, Ti, Td

class RootLocusDesigner:
    """Encapsulates design scan + plotting helpers."""
    def __init__(self, cfg: RootLocusConfig):
        self.cfg = cfg

    # --- plant ---
    def build_plant(self) -> ct.TransferFunction:
        if self.cfg.example == 'ogata_8_1':
            return ct.TransferFunction([1.0], [1.0, 6.0, 5.0, 0.0])  # 1/[s(s+1)(s+5)]
        if self.cfg.num is not None and self.cfg.den is not None:
            return ct.TransferFunction(parse_poly(self.cfg.num), parse_poly(self.cfg.den))
        raise ValueError("Provide cfg.example='ogata_8_1' or cfg.num/cfg.den.")

    # --- scan ---
    def zeta_list(self) -> List[float]:
        if self.cfg.zeta_values:
            return [z for z in self.cfg.zeta_values if 0 < z < 1]
        if self.cfg.zeta_range:
            zmin, zmax = self.cfg.zeta_range
            if not (0 < zmin < zmax < 1):
                raise ValueError("zeta_range must satisfy 0<ZMIN<ZMAX<1")
            return list(np.linspace(zmin, zmax, int(self.cfg.zeta_n)))
        return [0.60, 0.65, 0.67, 0.70]

    def compute_scan(self, Gp: ct.TransferFunction) -> List[DesignPoint]:
        wmin, wmax, wnum = self.cfg.omega
        rows: List[DesignPoint] = []
        for z in self.zeta_list():
            alpha = z / math.sqrt(1 - z*z)
            for w in np.linspace(max(1e-6, wmin), wmax, int(wnum)):
                s = complex(-alpha*w, w)
                gp_angle = complex_arg(ct.evalfr(Gp, s))
                s_angle  = complex_arg(s)
                a_list = _solve_a_on_ray(s, gp_angle, s_angle, kmin=self.cfg.kmin, kmax=self.cfg.kmax)
                if not a_list:
                    continue
                a = min(a_list)
                K, Kp, Ti, Td = _gain_from_magnitude(s, a, Gp)
                rows.append(DesignPoint(zeta=z, omega=w, a=a, K=K, Kp=Kp, Ti=Ti, Td=Td,
                                        sigma=s.real, jw=s.imag))
        return rows

    @staticmethod
    def summarize_a(points: List[DesignPoint]) -> dict:
        if not points:
            return {"a_recommended": None, "count": 0}
        a_vals = np.array([p.a for p in points])
        q1, q3 = np.percentile(a_vals, [25, 75])
        iqr = q3 - q1
        lo, hi = q1 - 1.0*iqr, q3 + 1.0*iqr
        filt = a_vals[(a_vals > max(1e-8, lo)) & (a_vals < hi)]
        if filt.size == 0: filt = a_vals
        med = float(np.median(filt))
        q1n, q3n = float(np.percentile(filt, 25)), float(np.percentile(filt, 75))
        return {"a_recommended": med, "a_q1": q1n, "a_q3": q3n, "count": int(len(filt))}

    # --- plotting helpers ---
    @staticmethod
    def choose_axes_limits(example: Optional[str], branches: np.ndarray,
                           xlim_arg: Optional[tuple[float, float]],
                           ylim_arg: Optional[tuple[float, float]]):
        if xlim_arg is not None and len(xlim_arg) == 2:
            xlim = (float(xlim_arg[0]), float(xlim_arg[1]))
        elif example == "ogata_8_1":
            xlim = (-10.0, 2.0)
        else:
            xr = branches.real; xmin, xmax = np.nanmin(xr), np.nanmax(xr)
            pad = 0.05*(xmax - xmin if xmax > xmin else 1.0); xlim = (xmin - pad, xmax + pad)

        if ylim_arg is not None and len(ylim_arg) == 2:
            ylim = (float(ylim_arg[0]), float(ylim_arg[1]))
        elif example == "ogata_8_1":
            ylim = (-8.0, 8.0)
        else:
            yi = branches.imag; ymin, ymax = np.nanmin(yi), np.nanmax(yi)
            pad = 0.05*(ymax - ymin if ymax > ymin else 1.0); ylim = (ymin - pad, ymax + pad)

        return xlim, ylim

    @staticmethod
    def make_pid_tf(Kp, Ti, Td):
        Ki = 0.0 if (Ti in (0, float('inf'))) else (Kp / Ti)
        Kd = Kp * Td
        return ct.TransferFunction([Kd, Kp, Ki], [1, 0])

    @staticmethod
    def analyze_closed_loop(Gp, Kp, Ti, Td, settle=0.02, Tfinal=None) -> dict:
        """
        Compute basic closed-loop performance metrics using the non-deprecated
        python-control APIs (tested on control==0.10.2).
        """
        Gc = RootLocusDesigner.make_pid_tf(Kp, Ti, Td)
        L = Gc * Gp
        T = ct.feedback(L, 1)

        # Estimate a reasonable simulation horizon.
        if Tfinal is None:
            # Prefer the non-deprecated plural form; retain a tiny fallback.
            try:
                poles = ct.poles(T)
            except AttributeError:  # very old control versions fallback
                poles = ct.pole(T)
            poles = np.asarray(poles)
            neg = -np.real(poles[np.real(poles) < 0])
            tau = 1.0 / (np.min(neg) if neg.size else 1.0)
            Tfinal = max(8.0, 10 * tau)

        t, y = ct.step_response(T, T=np.linspace(0, Tfinal, 1500))
        yss = y[-1]

        peak = float(np.max(y))
        Mp = max(0.0, (peak - yss) / max(1e-12, yss)) * 100.0

        band = settle * abs(yss)
        idx = np.where(np.abs(y - yss) <= band)[0]
        Ts = None
        if idx.size:
            for i in idx:
                if np.all(np.abs(y[i:] - yss) <= band):
                    Ts = float(t[i])
                    break

        y10, y90 = 0.1 * yss, 0.9 * yss
        t10 = next((float(t[i]) for i in range(len(y)) if y[i] >= y10), None)
        t90 = next((float(t[i]) for i in range(len(y)) if y[i] >= y90), None)
        Tr = (t90 - t10) if (t10 is not None and t90 is not None) else None

        gm, pm, wg, wp = ct.margin(L)
        return dict(
            Mp=float(Mp),
            Ts=None if Ts is None else float(Ts),
            Tr=None if Tr is None else float(Tr),
            yss=float(yss),
            gm=float(gm),
            pm=float(pm),
            wg=float(wg),
            wp=float(wp),
        )

    # --- high-level helper for plotting computations ---
    def prepare_l_and_rays(self, Gp, a_for_plot: float):
        Gc = ct.TransferFunction([1, 2*a_for_plot, a_for_plot*a_for_plot], [1, 0])
        L = Gc * Gp
        branches, _ = rlocus_map(L)

        # axes
        xlim, ylim = self.choose_axes_limits(self.cfg.example, branches, self.cfg.xlim, self.cfg.ylim)

        # rays (clip to ylim or derived magnitude)
        if ylim is None:
            ymax = float(np.nanmax(np.abs(branches.imag))) if branches.size else 5.0
            wmax_ray = max(self.cfg.ray_wmin + 1e-6, self.cfg.ray_scale * ymax)
            yabs = wmax_ray
        else:
            yabs = max(abs(ylim[0]), abs(ylim[1]))
        wmin_ray = max(0.0, self.cfg.ray_wmin)
        wmax_ray = max(wmin_ray + 1e-6, yabs)
        rays = [(z, _zeta_line_points(z, wmin_ray, wmax_ray)) for z in self.zeta_list()]

        return L, branches, rays, xlim, ylim
