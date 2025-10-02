from __future__ import annotations
import logging, sys, os, math, warnings
from typing import Any, Dict, List, Optional, Sequence, Tuple
import numpy as np

_EPS = 1e-16

def build_logger(name: str = "plotTool", level=logging.INFO) -> logging.Logger:
    log = logging.getLogger(name)
    if not log.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        log.addHandler(h)
    # Default to INFO if level is None
    if level is None:
        level = logging.INFO
    log.setLevel(level)
    return log

def db(x: np.ndarray, eps: float = _EPS) -> np.ndarray:
    x = np.asarray(x, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        y = 20.0 * np.log10(np.maximum(x, eps))
    return y

def parse_list(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.replace(";", ",").split(",") if x.strip()], float)

def parse_roots(s: Optional[str]) -> List[complex]:
    if not s or not s.strip(): return []
    toks = [t for t in s.replace(";", ",").split(",") if t.strip()]
    out: List[complex] = []
    for t in toks:
        tt = t.strip().lower().replace("i", "j")
        if tt == "j": tt = "1j"
        out.append(complex(tt) if "j" in tt else float(tt))
    return out

def parse_matrix(s: str) -> np.ndarray:
    rows = [r.strip() for r in s.split(";") if r.strip()]
    return np.array([[float(x) for x in r.split(",") if x.strip()] for r in rows], float)

def parse_csv_vals(s: Optional[str]) -> Optional[List[float]]:
    if not s: return None
    return [float(x.strip()) for x in s.replace(";", ",").split(",") if x.strip()]

# --------------------- s‑polynomial / factors ---------------------
def _poly_from_s_expr(expr: str) -> np.ndarray:
    e = expr.strip()
    if e.startswith("(") and e.endswith(")"): e = e[1:-1]
    e = e.replace(" ", "").replace("−", "-")
    if not e: return np.array([0.0])
    parts = e.replace("-", "+-").split("+")
    parts = [p for p in parts if p]
    coeff_by_pow: Dict[int, float] = {}
    for t in parts:
        if "s" not in t:
            coeff_by_pow[0] = coeff_by_pow.get(0, 0.0) + float(t)
            continue
        i = t.find("s")
        a = t[:i]
        rest = t[i+1:]
        if a in ("", "+"): coef = 1.0
        elif a == "-":     coef = -1.0
        else:
            if a.endswith("*"): a = a[:-1]
            coef = float(a)
        p = 1
        if rest:
            if rest[0] != "^":
                raise ValueError(f"Bad term '{t}' in '{expr}'")
            p = int(rest[1:])
        coeff_by_pow[p] = coeff_by_pow.get(p, 0.0) + coef
    maxp = max(coeff_by_pow) if coeff_by_pow else 0
    c = np.zeros(maxp+1, float)
    for pow_k, val in coeff_by_pow.items():
        c[maxp - pow_k] = val
    if 0 in coeff_by_pow:
        c[-1] = coeff_by_pow[0]
    nz = np.nonzero(np.abs(c) > 0)[0]
    return c[nz[0]:] if nz.size else np.array([0.0])

def _split_top_factors(spec: str) -> List[str]:
    toks: List[str] = []
    buf: List[str] = []
    depth = 0
    for ch in spec:
        if ch == "(":
            depth += 1; buf.append(ch)
        elif ch == ")":
            depth = max(0, depth-1); buf.append(ch)
        elif (ch == " " or ch == "*") and depth == 0:
            if buf: toks.append("".join(buf).strip()); buf = []
        else:
            buf.append(ch)
    if buf: toks.append("".join(buf).strip())
    return [t for t in toks if t and t != "+"]

def _parse_factor_token(tok: str, Kval: float) -> np.ndarray:
    t = tok.strip()
    if not t: return np.array([1.0])
    if t.upper() == "K": return np.array([float(Kval)], float)
    if t.startswith("(") and t.endswith(")"):
        inner = t[1:-1].strip()
        return _poly_from_s_expr(inner) if ("s" in inner or "S" in inner) else parse_list(inner)
    if "s" in t or "S" in t: return _poly_from_s_expr(t)
    if t in ("+","-"):
        raise ValueError("Standalone '+' or '-' is not a factor; wrap polynomials in parentheses.")
    return np.array([float(t)], float)

def parse_factors(spec: Optional[str], Kval: float = 1.0) -> np.ndarray:
    if not spec or not spec.strip(): return np.array([1.0])
    s = spec.strip().replace(")(", ")*(")
    tokens = _split_top_factors(s)
    poly = np.array([1.0], float)
    for tok in tokens:
        f = _parse_factor_token(tok, Kval).astype(float)
        poly = np.polymul(poly, f)
    nz = np.nonzero(np.abs(poly) > 0)[0]
    return poly[nz[0]:] if nz.size else np.array([0.0])

# --------------------- TF helpers ---------------------
def parse_range4(arg: Optional[str]):
    if not arg: return None
    s = arg.replace(";", ",")
    vals = [v for v in s.split(",") if v.strip()]
    if len(vals) != 4: return None
    try:
        return (float(vals[0]), float(vals[1]), float(vals[2]), float(vals[3]))
    except Exception:
        return None
