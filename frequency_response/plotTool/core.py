from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Tuple, List, Optional
import numpy as np
import math
import control as ct

from .design import tf_arrays
from .utils import db

def _eval_tf(G: ct.TransferFunction, w: np.ndarray) -> np.ndarray:
    n, d = tf_arrays(G)
    s = 1j * np.asarray(w, float)
    N = np.polyval(n, s)
    D = np.polyval(d, s)
    return N / D

def bode_data(G: ct.TransferFunction, w: np.ndarray):
    Hjw = _eval_tf(G, w)
    mag = np.abs(Hjw)
    ph = np.unwrap(np.angle(Hjw))
    return mag, ph, w

def make_grid(G: ct.TransferFunction, wmin: Optional[float], wmax: Optional[float], npts: int) -> np.ndarray:
    breaks: List[float] = []
    try:
        num, den = tf_arrays(G)
        z = np.roots(num) if num.size > 1 else np.array([])
        p = np.roots(den)
        cand = np.concatenate([z, p])
        for s in np.atleast_1d(cand):
            if np.isfinite(s):
                w = abs(s)
                if w > 0: breaks.append(float(w))
    except Exception:
        pass
    br = np.sort(np.array(breaks)) if breaks else np.array([])
    if wmin is None:
        wmin = max(1e-3, float(np.min(br)/10) if br.size else 1e-2)
    if wmax is None:
        wmax = float(np.max(br)*10) if br.size else 1e2
        if wmax < 10*wmin: wmax = 10*wmin
    npts = int(max(128, npts))
    w = np.logspace(np.log10(max(1e-6, float(wmin))),
                    np.log10(max(float(wmax), float(wmin)*1.0001)), npts)
    return w

@dataclass
class Margins:
    gm: float
    gm_db: float
    pm: float
    wgc: float
    wpc: float

@dataclass
class CLMetrics:
    Mr_db: float
    wr: float
    wb: float
    L_wr_phi: float
    L_wr_db: float
    L_wb_phi: float
    L_wb_db: float

def _cross_estimates(w: np.ndarray, mag: np.ndarray, ph_deg: np.ndarray):
    wgc = float("nan"); wpc = float("nan"); pm = float("nan"); gm = float("inf")
    for k in range(len(w)-1):
        if (mag[k]-1)*(mag[k+1]-1) <= 0:
            t = (1 - mag[k]) / (mag[k+1] - mag[k] + 1e-16)
            wgc = float(w[k] + t*(w[k+1]-w[k])); pm = 180.0 + float(np.interp(wgc, w, ph_deg))
            break
    for k in range(len(w)-1):
        if (ph_deg[k]+180.0)*(ph_deg[k+1]+180.0) <= 0:
            t = (-180.0 - ph_deg[k]) / (ph_deg[k+1] - ph_deg[k] + 1e-16)
            wpc = float(w[k] + t*(w[k+1]-w[k]))
            mag_at = float(np.interp(wpc, w, mag))
            gm = (1.0/mag_at) if mag_at > 0 else float("inf")
            break
    return gm, pm, wgc, wpc

def compute_margins(L: ct.TransferFunction, w: np.ndarray) -> Margins:
    mag, ph, ww = bode_data(L, w)
    ph_deg = np.degrees(ph)
    gm, pm, wgc, wpc = _cross_estimates(ww, mag, ph_deg)
    try:
        out = ct.margin(L)
        if isinstance(out, (list, tuple)) and len(out) >= 2:
            if np.isfinite(out[0]): gm = float(out[0])
            if np.isfinite(out[1]): pm = float(out[1])
    except Exception:
        pass
    gm_db = (20*np.log10(gm) if (gm > 0 and np.isfinite(gm)) else float("inf"))
    return Margins(float(gm), float(gm_db), float(pm), float(wgc), float(wpc))

def closedloop_metrics(L: ct.TransferFunction, w: np.ndarray) -> CLMetrics:
    T = ct.minreal(ct.feedback(L, 1), verbose=False)
    magT, _, ww = bode_data(T, w)
    idx = int(np.argmax(magT))
    Mr = float(magT[idx]); wr = float(ww[idx])
    Mr_db = 20*np.log10(Mr) if Mr > 0 else -np.inf
    m0 = float(magT[0]); target = m0 / math.sqrt(2.0)
    wb = float("nan")
    for i in range(len(ww)-1):
        if (magT[i]-target)*(magT[i+1]-target) <= 0:
            t = (target - magT[i]) / (magT[i+1]-magT[i] + 1e-16)
            wb = float(ww[i] + t*(ww[i+1]-ww[i])); break
    Lmag, Lph, _ = bode_data(L, np.array([wr, wb]))
    Lph_deg = np.degrees(Lph)
    L_wr_db = float(db(np.array([Lmag[0]]))[0]); L_wr_phi = float(Lph_deg[0])
    L_wb_db = float(db(np.array([Lmag[1]]))[0]) if np.isfinite(wb) else float("nan")
    L_wb_phi = float(Lph_deg[1]) if np.isfinite(wb) else float("nan")
    return CLMetrics(float(Mr_db), wr, wb, L_wr_phi, L_wr_db, L_wb_phi, L_wb_db)

def nyq_encirclements(L: ct.TransferFunction, w: np.ndarray, center=(-1.0, 0.0)) -> int:
    Hjw = _eval_tf(L, w)
    track = np.concatenate([Hjw, np.conjugate(Hjw[-2:0:-1])])
    z = track - (center[0] + 1j*center[1])
    mask = np.isfinite(z); z = z[mask]
    if z.size < 2: return 0
    ang = np.unwrap(np.angle(z)); dtheta = ang[-1] - ang[0]
    val = -dtheta / (2*math.pi)
    if not np.isfinite(val): return 0
    return int(round(val))

# ---------------- Nichols grid ----------------
_M_LEVELS_DB_DEFAULT = [-40,-20,-12,-6,-3,-1,-0.5,-0.25,0.25,0.5,1,3,5,6,9,12,20,40]
_N_ALPHAS_DEG_DEFAULT = [-120,-90,-80,-70,-60,-50,-45,-40,-30,-20,-10,0,10,20,30,40,45,50,60,70,80]

def nichols_defaults():
    return list(_M_LEVELS_DB_DEFAULT), list(_N_ALPHAS_DEG_DEFAULT)

def nichols_M_grid(xphase_deg: np.ndarray, levels_db: Sequence[float], y_limits: Tuple[float,float]):
    out = []
    th = np.radians(xphase_deg); ymin, ymax = y_limits
    for MdB in levels_db:
        if abs(MdB) < 1e-12: continue
        M = 10**(MdB/20.0); M2 = M*M
        base = 1.0 - (M2)*(np.sin(th)**2)
        root_safe = np.full_like(base, np.nan, dtype=float)
        ok = base >= 0; root_safe[ok] = np.sqrt(base[ok])
        num_plus  = -M2*np.cos(th) + (M * root_safe)
        num_minus = -M2*np.cos(th) - (M * root_safe)
        den = (M2 - 1.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            r1 = np.abs(num_plus / den); r2 = np.abs(num_minus / den)
        for r in (r1, r2):
            r = np.where(np.isfinite(r) & (r > 0), r, np.nan)
            y = db(r); y = np.clip(y, ymin, ymax)
            out.append((xphase_deg.copy(), y, f"{MdB:g} dB"))
    return out

def nichols_N_grid(xphase_deg: np.ndarray, alphas_deg: Sequence[float], y_limits: Tuple[float,float]):
    out = []
    th = np.radians(xphase_deg); ymin, ymax = y_limits
    for alpha in alphas_deg:
        ta = np.tan(th - math.radians(alpha))
        denom = (np.sin(th) - ta*np.cos(th))
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.abs(ta / denom)
        r = np.where(np.isfinite(r) & (r > 0), r, np.nan)
        y = db(r); y = np.clip(y, ymin, ymax)
        out.append((xphase_deg.copy(), y, f"{alpha}°"))
    return out


# ---------------- Static constants (unity feedback) ----------------
def _s_zero_mult(poly: np.ndarray, tol=1e-14) -> int:
    k = 0
    for coef in poly[::-1]:
        if abs(coef) < tol: k += 1
        else: break
    return k

def static_constants(G: ct.TransferFunction):
    """(Kp, Kv, Ka) using analytic limits around s=0 for unity feedback."""
    num, den = tf_arrays(G)
    n0 = _s_zero_mult(num)
    d0 = _s_zero_mult(den)
    m = min(n0, d0)
    n_red = num[:len(num)-m] if m > 0 else num
    d_red = den[:len(den)-m] if m > 0 else den
    type_p = _s_zero_mult(d_red)  # remaining integrators

    d_base = d_red[:len(d_red)-type_p] if type_p > 0 else d_red
    if d_base.size == 0:
        return (float("inf"), float("inf"), float("inf"))
    N0 = float(n_red[-1])
    D0 = float(d_base[-1])
    R0 = N0 / D0 if abs(D0) > 0 else float("inf")

    def pick(p: int, m: int) -> float:
        if p < m: return 0.0
        if p == m: return R0
        return float("inf")

    Kp = pick(type_p, 0); Kv = pick(type_p, 1); Ka = pick(type_p, 2)
    return Kp, Kv, Ka
