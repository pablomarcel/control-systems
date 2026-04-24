from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import math
import numpy as np
import sympy as sp
try:
    import control as ct
    from control.timeresp import step_response
except Exception as e:  # pragma: no cover
    ct = None
    step_response = None  # type: ignore

# Optional plotting flags (checked in plotter)
MPL_OK = True
PLOTLY_OK = True
try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception:
    MPL_OK = False
try:
    import plotly.graph_objects as go  # type: ignore
except Exception:
    PLOTLY_OK = False

# ------------------------------ Domain Models ------------------------------

@dataclass(slots=True)
class Metrics:
    overshoot: float
    settling_time: float
    rise_time: float
    ess: float
    itae: float
    ise: float
    tfinal_used: float

@dataclass(slots=True)
class Requirements:
    max_overshoot: Optional[float] = None
    max_settling: Optional[float] = None
    max_rise: Optional[float] = None
    max_ess: Optional[float] = None
    settle_tol: float = 0.02

@dataclass(slots=True)
class Candidate:
    params: Dict[str, float]
    metrics: Metrics
    obj: float
    stable: bool
    controller_str: str

# ------------------------------- TF Builders -------------------------------

def poly_from_string(expr: str, s_symbol: sp.Symbol) -> List[float]:
    sym = sp.sympify(expr, locals={str(s_symbol): s_symbol})
    poly = sp.Poly(sp.expand(sym), s_symbol)
    return [float(c) for c in poly.all_coeffs()]

def tf_from_args(args) -> "ct.TransferFunction":
    if ct is None:
        raise RuntimeError("python-control is required")
    s = sp.Symbol("s")
    if args.plant_form == "coeff":
        return ct.tf(_parse_floats(args.num), _parse_floats(args.den))
    if args.plant_form == "poly":
        num = poly_from_string(args.num_poly, s)
        den = poly_from_string(args.den_poly, s)
        return ct.tf(num, den)
    if args.plant_form == "zpk":
        zeros = _parse_complex(args.zeros)
        poles = _parse_complex(args.poles)
        gain = 1.0 if args.gain is None else float(args.gain)
        zpk_sys = ct.zpk(zeros, poles, gain)
        return ct.tf(zpk_sys)
    raise ValueError(f"unknown plant_form {args.plant_form}")

def controller_tf(structure: str, pars: Dict[str, float]) -> "ct.TransferFunction":
    s = ct.TransferFunction.s
    if structure == "pid":
        return pars["Kp"] + pars["Ki"]/s + pars["Kd"]*s
    if structure == "pi":  return pars["Kp"] + pars["Ki"]/s
    if structure == "pd":  return pars["Kp"] + pars["Kd"]*s
    if structure == "pid_dz":
        return pars["K"] * (s + pars["a"])**2 / s
    raise ValueError(f"unknown structure {structure}")

def pretty_tf(name: str, G: "ct.TransferFunction") -> str:
    return f"{name}:\n{G}"

# ------------------------------- Computations -------------------------------

def compute_metrics(sys_cl: "ct.TransferFunction",
                    tfinal: Optional[float] = None,
                    dt: Optional[float] = None,
                    settle_tol: float = 0.02) -> Metrics:
    if ct is None:
        raise RuntimeError("python-control is required")
    # pick horizon
    if tfinal is None:
        p = np.array(ct.poles(sys_cl), dtype=complex)
        if p.size == 0:
            tfinal = 10.0
        else:
            max_real = float(np.max(p.real))
            if max_real < 0:
                sigma = -max_real
                tau = 1.0 / max(1e-6, sigma)
            else:
                tau = 10.0
            tfinal = float(np.clip(10.0 * tau, 5.0, 120.0))
    if dt is None:
        dt = float(tfinal) / 2000.0

    T = np.arange(0.0, float(tfinal) + float(dt), float(dt))
    T, y = step_response(sys_cl, T)
    y_final = float(y[-1])
    err = 1.0 - y
    ess = abs(1.0 - y_final)

    y_peak = float(np.max(y))
    denom = max(1e-12, abs(y_final))
    overshoot = max(0.0, 100.0 * (y_peak - y_final) / denom)

    band = settle_tol * abs(y_final)
    idx = np.where(np.abs(y - y_final) > band)[0]
    settling_time = 0.0 if idx.size == 0 else float(T[min(idx[-1] + 1, len(T) - 1)])

    try:
        lo, hi = 0.1 * y_final, 0.9 * y_final
        t_lo = float(T[np.where(y >= lo)[0][0]])
        t_hi = float(T[np.where(y >= hi)[0][0]])
        rise_time = max(0.0, t_hi - t_lo)
    except Exception:
        rise_time = float("nan")

    ise = float(np.trapezoid(err**2, T))
    itae = float(np.trapezoid(np.abs(err) * T, T))

    return Metrics(overshoot, settling_time, rise_time, ess, itae, ise, float(T[-1]))

def meets_requirements(m: Metrics, r: Requirements) -> bool:
    if r.max_overshoot is not None and m.overshoot > r.max_overshoot + 1e-12: return False
    if r.max_settling is not None and m.settling_time > r.max_settling + 1e-12: return False
    if r.max_rise is not None and m.rise_time > r.max_rise + 1e-12: return False
    if r.max_ess is not None and m.ess > r.max_ess + 1e-12: return False
    return True

def objective_value(m: Metrics, name: str,
                    w_ts: float = 1.0, w_mp: float = 1.0,
                    w_itae: float = 1.0, w_ise: float = 1.0) -> float:
    key = name.lower()
    if key == "ts": return m.settling_time
    if key == "mp": return m.overshoot
    if key == "itae": return m.itae
    if key == "ise": return m.ise
    if key == "weighted":
        return w_ts*m.settling_time + w_mp*m.overshoot + w_itae*m.itae + w_ise*m.ise
    return m.itae

def poles_stable(sys: "ct.TransferFunction") -> bool:
    p = ct.poles(sys)
    return (len(p) == 0) or (np.max(np.real(p)) < 0.0)

def margins_report(L: "ct.TransferFunction") -> str:
    def _fmt_num(x):
        try:
            import numpy as _np, math as _math
            if x is None: return "n/a"
            if _np.size(x) > 1: x = _np.asarray(x).flat[0]
            x = float(x)
            if _math.isinf(x): return "inf"
            if _math.isnan(x): return "nan"
            return f"{x:.4g}"
        except Exception:
            return str(x)
    gm = pm = wgc = wpc = None
    try:
        mres = ct.margin(L)
        if isinstance(mres, tuple):
            if len(mres) >= 4:
                gm, pm, wgc, wpc = mres[:4]
            elif len(mres) == 3:
                gm, pm, wgc = mres
        else:
            gm = getattr(mres, "gm", None)
            pm = getattr(mres, "pm", None)
            wgc = getattr(mres, "wgc", None)
            wpc = getattr(mres, "wpc", None)
    except Exception:
        pass
    sm_text = ""
    try:
        sres = ct.stability_margins(L)
        if isinstance(sres, tuple) and len(sres) >= 3:
            sm, wg, wp = sres[:3]
            sm_text = f"\nStability margin (SM): {_fmt_num(sm)} @ ω≈{_fmt_num(wg)} / {_fmt_num(wp)}"
        else:
            sm = getattr(sres, "sm", None)
            wg = getattr(sres, "wgm", None)
            wp = getattr(sres, "wpm", None)
            if sm is not None:
                sm_text = f"\nStability margin (SM): {_fmt_num(sm)} @ ω≈{_fmt_num(wg)} / {_fmt_num(wp)}"
    except Exception:
        pass
    return (
        f"Gain margin (GM): {_fmt_num(gm)} (linear) @ ω_gc={_fmt_num(wgc)} rad/s\n"
        f"Phase margin (PM): {_fmt_num(pm)} deg @ ω_pc={_fmt_num(wpc)} rad/s"
        f"{sm_text}"
    )

# ------------------------------- Helpers -----------------------------------
def _parse_floats(s: str | None):
    if not s: return []
    return [float(x) for x in s.replace(",", " ").split()]
def _parse_complex(s: str | None):
    if not s: return []
    toks = s.replace(",", " ").replace("i", "j").split()
    return [complex(tok) for tok in toks]
