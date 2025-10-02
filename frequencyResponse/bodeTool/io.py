from __future__ import annotations
from typing import List, Dict
import numpy as np

def parse_list(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.replace(";", ",").split(",") if x.strip()], dtype=float)

def _maybe_complex(x: str) -> complex:
    x = x.strip().lower().replace("i", "j")
    if x == "j":
        x = "1j"
    if "j" in x:
        return complex(x)
    return float(x)

def parse_roots(s: str | None) -> List[complex]:
    if not s or not s.strip():
        return []
    tokens = [t for t in s.replace(";", ",").split(",") if t.strip()]
    return [_maybe_complex(t) for t in tokens]

def poly_from_s_expr(expr: str) -> np.ndarray:
    e = expr.strip()
    if e.startswith("(") and e.endswith(")"):
        e = e[1:-1].strip()
    e = e.replace(" ", "")
    if e.startswith("+"):
        e = e[1:]
    parts = e.replace("-", "+-").split("+")
    terms = [p for p in parts if p]

    coeff_by_pow: Dict[int, float] = {}
    for t in terms:
        if "s" not in t:
            c = float(t)
            coeff_by_pow[0] = coeff_by_pow.get(0, 0.0) + c
            continue
        i = t.find("s")
        coef_str = t[:i]
        rest = t[i+1:]
        if coef_str in ("", "+"):
            coef = 1.0
        elif coef_str == "-":
            coef = -1.0
        else:
            if coef_str.endswith("*"):
                coef_str = coef_str[:-1]
            coef = float(coef_str)
        power = 1
        if rest:
            if rest[0] == "^":
                power = int(rest[1:])
            else:
                raise ValueError(f"Bad s-term '{t}' in '{expr}'")
        coeff_by_pow[power] = coeff_by_pow.get(power, 0.0) + coef

    max_pow = max(coeff_by_pow.keys()) if coeff_by_pow else 0
    c = np.zeros(max_pow+1, dtype=float)
    for p, val in coeff_by_pow.items():
        c[max_pow - p] = val
    if 0 in coeff_by_pow:
        c[-1] = coeff_by_pow[0]
    return c

def _parse_factor_token(tok: str, Kval: float) -> np.ndarray:
    t = tok.strip()
    if not t:
        return np.array([1.0])
    if t[0] == "(" and t[-1] == ")":
        inner = t[1:-1].strip()
        if "s" in inner or "S" in inner:
            return poly_from_s_expr(inner)
        return parse_list(inner)
    if t.upper() == "K":
        return np.array([float(Kval)], dtype=float)
    if "s" in t or "S" in t:
        return poly_from_s_expr(t)
    return np.array([float(t)])

def parse_factors(spec: str | None, Kval: float = 1.0) -> np.ndarray:
    if not spec or not spec.strip():
        return np.array([1.0])
    tmp = spec.replace("*", " ")
    tokens = [t for t in tmp.split() if t.strip()]
    poly = np.array([1.0])
    for tok in tokens:
        f = _parse_factor_token(tok, Kval)
        poly = np.polymul(poly, f.astype(float))
    return poly
