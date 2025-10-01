from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any
import math
import numpy as np
import sympy as sp
from .utils import parse_list, parse_matrix

# external deps (no heavy work at import time)
try:
    import control as ctrl
except Exception as e:  # pragma: no cover
    raise SystemExit("Please install python-control: pip install control\n" + str(e))

def tf_siso_arrays(sys: "ctrl.TransferFunction") -> Tuple[np.ndarray, np.ndarray]:
    num, den = ctrl.tfdata(sys)
    try:
        n = np.asarray(num[0][0], dtype=float)
        d = np.asarray(den[0][0], dtype=float)
    except Exception:
        n = np.asarray(num, dtype=float).squeeze()
        d = np.asarray(den, dtype=float).squeeze()
    return n, d

def poles_and_zeros(sys: "ctrl.TransferFunction"):
    P = np.asarray(ctrl.poles(sys) if hasattr(ctrl, "poles") else ctrl.pole(sys))
    Z = np.asarray(ctrl.zeros(sys) if hasattr(ctrl, "zeros") else ctrl.zero(sys))
    return P, Z

@dataclass(slots=True)
class L0Builder:
    """Build open-loop L0(s) from TF / ZPK / Series / State-space."""
    def build(self, **cfg) -> "ctrl.TransferFunction":
        # State-space precedence
        if cfg.get("ssA") and cfg.get("ssB") and cfg.get("ssC"):
            A = parse_matrix(cfg["ssA"])
            B = parse_matrix(cfg["ssB"])
            C = parse_matrix(cfg["ssC"])
            D = parse_matrix(cfg["ssD"]) if cfg.get("ssD") else np.zeros((C.shape[0], B.shape[1]))
            if A.shape[0] != A.shape[1]:
                raise ValueError("A must be square")
            if B.shape[0] != A.shape[0] or C.shape[1] != A.shape[1] or D.shape != (C.shape[0], B.shape[1]):
                raise ValueError("Incompatible shapes for A,B,C,D")
            ss = ctrl.ss(A, B, C, D)
            r, c = (cfg.get("io") or (0, 0))
            tf_mimo = ctrl.ss2tf(ss)
            if isinstance(tf_mimo, (list, tuple)):  # very old versions of control
                num, den = tf_mimo
                L0 = ctrl.tf(num[r][c], den[r][c])
            else:
                try:
                    L0 = tf_mimo[r, c]
                except Exception:
                    L0 = tf_mimo
            return ctrl.minreal(L0, verbose=False)

        # Series G(s)H(s)
        if cfg.get("Gnum") and cfg.get("Gden"):
            G = ctrl.tf(parse_list(cfg["Gnum"]), parse_list(cfg["Gden"]))
            H = ctrl.tf(parse_list(cfg["Hnum"]), parse_list(cfg["Hden"])) if (cfg.get("Hnum") and cfg.get("Hden")) else ctrl.tf([1],[1])
            return ctrl.minreal(G*H, verbose=False)

        # Direct TF
        if cfg.get("num") and cfg.get("den"):
            return ctrl.minreal(ctrl.tf(parse_list(cfg["num"]), parse_list(cfg["den"])), verbose=False)

        # ZPK
        z = parse_list(cfg.get("zeros"))
        p = parse_list(cfg.get("poles"))
        k = float(cfg.get("kgain", 1.0))
        return ctrl.minreal(ctrl.tf(ctrl.zpk(z, p, k)), verbose=False)

def poly_char(den: np.ndarray, num: np.ndarray, K: float) -> np.ndarray:
    n = max(len(den), len(num))
    D = np.pad(den, (n - len(den), 0))
    N = np.pad(num, (n - len(num), 0))
    return D + K * N

def connect_branches(roots_seq: List[np.ndarray]) -> np.ndarray:
    T = len(roots_seq)
    n = len(roots_seq[0])
    out = np.zeros((T, n), dtype=complex)
    out[0, :] = roots_seq[0]
    for t in range(1, T):
        prev = out[t - 1, :].copy()
        cur = roots_seq[t].copy()
        used = [False] * n
        for j in range(n):
            d = [abs(cur[i] - prev[j]) if not used[i] else np.inf for i in range(n)]
            i = int(np.argmin(d))
            out[t, j] = cur[i]
            used[i] = True
    return out

def jw_crossings(num: np.ndarray, den: np.ndarray) -> List[tuple[float, float]]:
    w = sp.symbols('w', real=True)
    s = sp.I * w
    Ns = sp.Poly(num.tolist(), sp.Symbol('s')).as_expr().subs({'s': s})
    Ds = sp.Poly(den.tolist(), sp.Symbol('s')).as_expr().subs({'s': s})
    NR, NI, DR, DI = sp.re(Ns), sp.im(Ns), sp.re(Ds), sp.im(Ds)
    try:
        eq = sp.simplify(DR * NI - DI * NR)
        if eq == 0:
            return []
        roots = sp.nroots(eq)
    except Exception:
        return []
    out: List[tuple[float, float]] = []
    for r in roots:
        if abs(sp.im(r)) < 1e-9 and float(sp.re(r)) >= 0.0:
            wv = float(sp.re(r))
            NRv = complex(sp.N(NR.subs({w: wv})))
            NIv = complex(sp.N(NI.subs({w: wv})))
            DRv = complex(sp.N(DR.subs({w: wv})))
            DIv = complex(sp.N(DI.subs({w: wv})))
            K = None
            if abs(NRv) > 1e-12:
                K = -(DRv / NRv).real
            elif abs(NIv) > 1e-12:
                K = -(DIv / NIv).real
            if K is not None and K > 0:
                out.append((wv, float(K)))
    out.sort(key=lambda t: t[0])
    return out

def real_axis_intervals(poles: np.ndarray, zeros: np.ndarray) -> List[tuple[float, float]]:
    xs = sorted([float(np.real_if_close(z)) for z in np.concatenate((poles, zeros)) if abs(z.imag) < 1e-12])
    pts = [-np.inf] + xs + [np.inf]
    ivs: List[tuple[float, float]] = []
    for a, b in zip(pts[:-1], pts[1:]):
        mid = (np.isfinite(a) and np.isfinite(b) and 0.5 * (a + b)) or ((b - 1.0) if not np.isfinite(a) else (a + 1.0))
        cnt = sum(1 for p in poles if abs(p.imag) < 1e-12 and np.real(p) > mid) + \
              sum(1 for z in zeros if abs(z.imag) < 1e-12 and np.real(z) > mid)
        if cnt % 2 == 1:
            ivs.append((a, b))
    return ivs

def break_points_poly(num: np.ndarray, den: np.ndarray, ivs: List[tuple[float, float]]) -> List[tuple[float, float]]:
    N = np.poly1d(num); D = np.poly1d(den)
    Q = np.polysub(np.polymul(N, np.polyder(D)), np.polymul(D, np.polyder(N)))
    q = np.real_if_close(Q.c).astype(float)
    q = q[np.argmax(np.abs(q) > 1e-14):] if np.any(np.abs(q) > 1e-14) else np.array([0.0])
    if len(q) <= 1:
        return []
    rr = np.roots(q)
    out: List[tuple[float, float]] = []
    for r in rr:
        if abs(r.imag) < 1e-9:
            s0 = float(r.real)
            on = any((s0 > iv[0] or not np.isfinite(iv[0])) and (s0 < iv[1] or not np.isfinite(iv[1])) for iv in ivs)
            if not on:
                continue
            Nv = N(s0); Dv = D(s0)
            if abs(Nv) < 1e-12:
                continue
            K = -Dv / Nv
            if K > 0:
                out.append((s0, float(K)))
    out.sort(key=lambda t: t[0])
    merged: List[tuple[float, float]] = []
    for s0, K0 in out:
        if not merged or abs(s0 - merged[-1][0]) > 1e-3:
            merged.append((s0, K0))
    return merged

class KGridBuilder:
    def auto_k_grid(self, num: np.ndarray, den: np.ndarray, zeros: np.ndarray) -> np.ndarray:
        Kset = {0.0}
        jws = jw_crossings(num, den)
        for _, Kc in jws:
            for f in (0.8, 1.0, 1.25):
                Kset.add(max(0.0, f * Kc))
        K_hi = max([K for _, K in jws], default=1.0) or 1.0
        if len(zeros):
            Kprobe = max(1.0, K_hi)
            for _ in range(8):
                r = np.roots(poly_char(den, num, Kprobe))
                ok = True
                for z in zeros:
                    if np.min(np.abs(r - z)) > 0.01 * max(1.0, abs(z)):
                        ok = False; break
                if ok:
                    break
                Kprobe *= 10.0
            K_hi = max(K_hi, Kprobe)
        K_hi = max(1.0, K_hi)
        dense = np.logspace(-6, math.log10(K_hi), 600)
        K = np.unique(np.concatenate((np.array(sorted(Kset)), dense)))
        return K

    def build(self,
              num: np.ndarray, den: np.ndarray, zeros: np.ndarray,
              kpos: Optional[tuple[float, float, int, str]],
              kneg: Optional[tuple[float, float]],
              auto_on: bool) -> np.ndarray:
        if kpos:
            lo, hi, N, mode = kpos
            if mode == "log":
                import numpy as _np
                Kpos = np.unique(np.concatenate(([0.0], _np.logspace(np.log10(max(lo, 1e-12)),
                                                                     np.log10(max(hi, 1e-12)), N))))
            else:
                Kpos = np.linspace(0.0, hi, N)
        else:
            Kpos = self.auto_k_grid(num, den, zeros) if auto_on else np.unique(np.concatenate(([0.0], np.logspace(-6, 3, 500))))
        if kneg:
            lo, hi = kneg
            Kneg = -np.logspace(np.log10(max(lo, 1e-12)), np.log10(max(hi, 1e-12)), max(60, len(Kpos) // 3))
            K = np.unique(np.concatenate((Kneg, Kpos)))
        else:
            K = Kpos
        return K

class RootLocusEngine:
    def roots_over_K(self, num: np.ndarray, den: np.ndarray, K: np.ndarray) -> np.ndarray:
        roots_seq = [np.roots(poly_char(den, num, k)) for k in K]
        return connect_branches(roots_seq)
