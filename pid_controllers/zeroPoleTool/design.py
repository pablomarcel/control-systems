from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional, Sequence, Tuple, Callable
import numpy as np
import control as ct

from .core import PlantPolys, plant_polys
from .utils import pick_tgrid_from_poles

from control.timeresp import step_response

@dataclass(slots=True, frozen=True)
class StepMetrics:
    overshoot: float
    settling_time: float
    rise_time: float
    ess: float
    tfinal_used: float

@dataclass(slots=True)
class Candidate:
    a: float; b: float; c: float
    Kc: float; z1: float; z0: float
    Gc1: ct.TransferFunction; Gc2: ct.TransferFunction; Gc_sum: ct.TransferFunction
    T_ref: ct.TransferFunction; T_dist: ct.TransferFunction
    metrics_ref: StepMetrics; metrics_dist: StepMetrics
    den_cl: List[float]
    dist_peak: float

def step_metrics(sys: ct.TransferFunction, settle_tol: float = 0.02) -> StepMetrics:
    t = pick_tgrid_from_poles(ct.poles(sys))
    t, y = step_response(sys, t)
    y = np.squeeze(np.asarray(y, dtype=float))
    y_final = float(y[-1]) if len(y) else 0.0
    y_peak = float(np.max(np.abs(y))) if len(y) else 0.0
    ess = abs(1.0 - y_final)
    if abs(y_final) > 1e-12:
        overshoot = max(0.0, 100.0 * (np.max(y) - y_final) / abs(y_final))
    else:
        overshoot = max(0.0, 100.0 * (np.max(y) - y_final) / max(1e-9, y_peak))
    band_base = max(abs(y_final), y_peak, 1e-3)
    band = settle_tol * band_base
    idx = np.where(np.abs(y - y_final) > band)[0]
    settling_time = 0.0 if idx.size == 0 else float(t[min(idx[-1] + 1, len(t) - 1)])
    try:
        if abs(y_final) > 1e-12:
            lo, hi = 0.1 * y_final, 0.9 * y_final
        else:
            lo, hi = 0.1 * y_peak, 0.9 * y_peak
        t_lo = float(t[np.where(y >= lo)[0][0]])
        t_hi = float(t[np.where(y >= hi)[0][0]])
        rise_time = max(0.0, t_hi - t_lo)
    except Exception:
        rise_time = float("nan")
    return StepMetrics(float(overshoot), float(settling_time), float(rise_time), float(ess), float(t[-1]))

# --- Architectures (Strategy pattern) ---

class Architecture:
    name: str
    def build_channels(self, a: float, b: float, c: float, P: PlantPolys) -> Tuple[ct.TransferFunction, ct.TransferFunction, ct.TransferFunction, ct.TransferFunction, ct.TransferFunction, List[float], float, float, float]:
        raise NotImplementedError

class Fig8_31(Architecture):
    name = "fig8-31"
    def build_channels(self, a,b,c,P: PlantPolys):
        den_cl = [1.0, 2.0*a + c, a*a + b*b + 2.0*a*c, (a*a + b*b)*c]
        if len(P.B) != 3:
            raise ValueError("This architecture currently supports deg(B)=2 plants.")
        b1, b0 = P.B[1], P.B[2]
        den_s2, den_s1, den_s0 = den_cl[1], den_cl[2], den_cl[3]
        Kc = (den_s2 - b1) / float(P.Kp)
        if not np.isfinite(Kc) or Kc <= 0:
            return None, None, None, None, None, den_cl, float(Kc), float("nan"), float("nan")  # type: ignore
        z1 = (den_s1 - b0) / (P.Kp * Kc)
        z0 = den_s0 / (P.Kp * Kc)
        s = ct.TransferFunction.s
        A_tf = ct.tf(P.A, [1.0])
        Gc_sum = (Kc*(s**2 + z1*s + z0)) / (s*A_tf)
        num_ref = den_s2*s**2 + den_s1*s + den_s0
        Gc1 = num_ref / (P.Kp * s * A_tf)
        Gc2 = Gc_sum - Gc1
        den_cl_poly = np.array(den_cl, dtype=float)
        A_s = np.array(P.A, dtype=float)
        num_dist = (P.Kp * np.convolve(A_s, [1.0, 0.0])).tolist()
        T_dist = ct.tf(num_dist, den_cl_poly)
        T_ref = ct.tf([den_s2, den_s1, den_s0], den_cl_poly)
        return Gc1, Gc2, Gc_sum, T_ref, T_dist, den_cl, float(Kc), float(z1), float(z0)

class Fig8_30(Architecture):
    name = "fig8-30"
    def build_channels(self, a,b,c,P: PlantPolys):
        den_cl = [1.0, 2.0*a + c, a*a + b*b + 2.0*a*c, (a*a + b*b)*c]
        if len(P.B) != 3:
            raise ValueError("This architecture currently supports deg(B)=2 plants.")
        b1, b0 = P.B[1], P.B[2]
        den_s2, den_s1, den_s0 = den_cl[1], den_cl[2], den_cl[3]
        gamma1 = (den_s2 - b1) / P.Kp
        alpha1 = (den_s1 - b0) / P.Kp
        beta1  = (den_s0) / P.Kp
        s = ct.TransferFunction.s
        A_tf = ct.tf(P.A, [1.0])
        Gc1 = (gamma1*s**2 + alpha1*s + beta1) / (s*A_tf)
        gamma = den_s2 / P.Kp
        alpha = den_s1 / P.Kp
        beta  = den_s0 / P.Kp
        Gc_sum = (gamma*s**2 + alpha*s + beta) / (s*A_tf)
        Gc2 = Gc_sum - Gc1
        if abs(gamma) > 0:
            Kc = float(gamma); z1 = float(alpha/gamma); z0 = float(beta/gamma)
        else:
            Kc, z1, z0 = float("nan"), float("nan"), float("nan")
        den_cl_poly = np.array(den_cl, dtype=float)
        A_s = np.array(P.A, dtype=float)
        num_dist = (P.Kp * np.convolve(A_s, [1.0, 0.0])).tolist()
        T_dist = ct.tf(num_dist, den_cl_poly)
        T_ref = ct.tf([den_s2, den_s1, den_s0], den_cl_poly)
        return Gc1, Gc2, Gc_sum, T_ref, T_dist, den_cl, Kc, z1, z0

ARCH_MAP = { "fig8-31": Fig8_31(), "fig8-30": Fig8_30() }

def linspace_or_vals(vals: List[float], rng: Tuple[float,float], n: int) -> List[float]:
    if vals:
        return sorted(set(float(v) for v in vals))
    lo, hi = float(rng[0]), float(rng[1])
    return list(np.linspace(lo, hi, int(n)))

class Designer:
    """Perform grid search and ranking for two-DOF zero placement."""
    def __init__(self, arch: str = "fig8-31"):
        if arch not in ARCH_MAP:
            raise ValueError(f"Unknown architecture '{arch}'")
        self.arch = ARCH_MAP[arch]

    def search(self, Gp: ct.TransferFunction, a_grid: List[float], b_grid: List[float], c_grid: List[float],
               os_min: float, os_max: float, ts_max: float, settle_tol: float,
               dist_peak_weight: float = 0.0, show_progress: bool = True, debug: bool = False):
        P = plant_polys(Gp)
        total = len(a_grid)*len(b_grid)*len(c_grid)
        ok_cands: List[Candidate] = []
        closest: List[Tuple[float, Tuple[float,float,float]]] = []
        counts = {k:0 for k in ["kcnonpos","unstable","metric_fails","ok","errors"]}

        iterator = ((a,b,c) for a in a_grid for b in b_grid for c in c_grid)
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(list(iterator), total=total, desc="Grid (a×b×c)", ncols=88)
            except Exception:
                pass

        for (a,b,c) in iterator:
            try:
                Gc1,Gc2,Gc_sum,T_ref,T_dist,den_cl,Kc,z1,z0 = self.arch.build_channels(a,b,c,P)
                if Gc1 is None:
                    counts["kcnonpos"] += 1
                    continue
                roots = np.roots(den_cl)
                if np.max(roots.real) >= 0 or not np.all(np.isfinite(roots)):
                    counts["unstable"] += 1
                    continue
                mr = step_metrics(T_ref, settle_tol=settle_tol)
                md = step_metrics(T_dist, settle_tol=settle_tol)
                ok = (os_min <= mr.overshoot <= os_max) and (mr.settling_time <= ts_max)
                if not ok:
                    pen = (
                        (0 if mr.overshoot >= os_min else (os_min - mr.overshoot))
                        + (0 if mr.overshoot <= os_max else (mr.overshoot - os_max))
                        + max(0.0, mr.settling_time - ts_max)
                    )
                    closest.append((pen, (a,b,c)))
                    counts["metric_fails"] += 1
                    continue
                ttmp = pick_tgrid_from_poles(ct.poles(T_dist))
                _, ytmp = step_response(T_dist, ttmp)
                peak = float(np.max(np.abs(np.asarray(ytmp, dtype=float))))
                ok_cands.append(Candidate(a=a,b=b,c=c,Kc=Kc,z1=z1,z0=z0,
                                          Gc1=Gc1,Gc2=Gc2,Gc_sum=Gc_sum,
                                          T_ref=T_ref,T_dist=T_dist,
                                          metrics_ref=mr,metrics_dist=md,
                                          den_cl=den_cl,dist_peak=peak))
                counts["ok"] += 1
            except Exception:
                counts["errors"] += 1
                continue

        best = None
        if ok_cands:
            band_mid = 0.5*(os_min + os_max)
            ok_cands.sort(key=lambda c: (abs(c.metrics_ref.overshoot - band_mid),
                                         c.metrics_ref.settling_time,
                                         dist_peak_weight*c.dist_peak))
            best = ok_cands[0]
        return best, ok_cands, closest, counts
