
# io.py — parsing & I/O helpers
from __future__ import annotations
from typing import List, Tuple, Optional
import json
import sympy as sp
from .utils import sym_s, to_expr_s

def parse_poly(arg: str | List[float]) -> List[sp.Expr]:
    """CSV '1,3,2' or poly string 's^2+3*s+2' → coeffs (descending powers, exact)."""
    if isinstance(arg, (list, tuple)):
        return [sp.nsimplify(v) for v in arg]
    txt = str(arg).strip()
    if any(ch in txt for ch in ('s','S','x','X','+','-','*','/','(',')','^')):
        poly = sp.Poly(sp.expand(to_expr_s(txt)), sym_s())
        return [sp.nsimplify(c) for c in poly.all_coeffs()]
    parts = [p for p in txt.replace(';', ',').split(',') if p.strip()]
    return [sp.nsimplify(p) for p in parts]

def parse_tf_string(tf_str: str) -> Tuple[List[sp.Expr], List[sp.Expr]]:
    expr = sp.together(to_expr_s(tf_str))
    num, den = sp.fraction(expr)
    Ps = sp.Poly(sp.expand(num), sym_s())
    Qs = sp.Poly(sp.expand(den), sym_s())
    return [sp.nsimplify(c) for c in Ps.all_coeffs()], [sp.nsimplify(c) for c in Qs.all_coeffs()]

def normalize_monic(num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> Tuple[List[sp.Expr], List[sp.Expr]]:
    """Make denominator monic."""
    den_lc = sp.nsimplify(den_desc[0])
    if den_lc == 0:
        raise ValueError("Denominator leading coefficient is zero.")
    num_desc = [sp.nsimplify(c/den_lc) for c in num_desc]
    den_desc = [sp.nsimplify(c/den_lc) for c in den_desc]
    return num_desc, den_desc

def ensure_proper(num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> Tuple[List[sp.Expr], List[sp.Expr], sp.Expr]:
    """If degN==degD, do long division to extract D (constant feedthrough)."""
    s = sym_s()
    Pn = sp.Poly(sp.expand(sp.Poly(num_desc, s).as_expr()), s)
    Pd = sp.Poly(sp.expand(sp.Poly(den_desc, s).as_expr()), s)
    if Pn.degree() > Pd.degree():
        raise ValueError("Improper TF: deg(num) > deg(den).")
    if Pn.degree() == Pd.degree():
        q, r = sp.div(Pn, Pd)
        if q.degree() > 0:
            raise ValueError("Quasi-improper: non-constant quotient.")
        Dfeed = sp.nsimplify(q.as_expr())
        num_desc = sp.Poly(r.as_expr(), s).all_coeffs()
        return num_desc, den_desc, Dfeed
    return num_desc, den_desc, sp.Integer(0)

def coeffs_asc(desc: List[sp.Expr], n: int) -> List[sp.Expr]:
    """Return ascending [a0 ... a_{n-1}] padded/truncated to length n."""
    asc = list(reversed(desc))
    if len(asc) < n:
        asc += [sp.Integer(0)]*(n - len(asc))
    elif len(asc) > n:
        asc = asc[:n]
    return [sp.nsimplify(c) for c in asc]

def parse_vec_csv(txt: Optional[str], n: int) -> sp.Matrix:
    if not txt:
        return sp.zeros(n, 1)
    parts = [p for p in txt.replace(';', ',').split(',') if p.strip()]
    vals = [sp.nsimplify(p) for p in parts]
    if len(vals) != n:
        raise ValueError(f"Expected {n} entries for the initial condition; got {len(vals)}.")
    return sp.Matrix(vals).reshape(n, 1)

def save_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
