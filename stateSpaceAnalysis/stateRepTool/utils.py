from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import sympy as sp

def sym_s() -> sp.Symbol:
    return sp.Symbol("s")

def to_expr(s: str) -> sp.Expr:
    s = s.replace("^", "**").replace("X", "s").replace("x", "s").replace("S", "s")
    return sp.sympify(s, locals={"s": sym_s()})

def parse_poly(arg: str | List[float]) -> List[sp.Expr]:
    """Parse CSV or polynomial string to descending-power coefficients (SymPy exact)."""
    if isinstance(arg, (list, tuple)):
        return [sp.nsimplify(v) for v in arg]
    txt = str(arg).strip()
    if any(ch in txt for ch in ('s','S','x','X','+','-','*','/','(',')','^')):
        poly = sp.Poly(sp.expand(to_expr(txt)), sym_s())
        return [sp.nsimplify(c) for c in poly.all_coeffs()]
    parts = [p for p in txt.replace(';', ',').split(',') if p.strip()]
    return [sp.nsimplify(p) for p in parts]

def parse_tf_string(tf_str: str) -> Tuple[List[sp.Expr], List[sp.Expr]]:
    expr = sp.together(to_expr(tf_str))
    num, den = sp.fraction(expr)
    Ps = sp.Poly(sp.expand(num), sym_s())
    Qs = sp.Poly(sp.expand(den), sym_s())
    return [sp.nsimplify(c) for c in Ps.all_coeffs()], [sp.nsimplify(c) for c in Qs.all_coeffs()]

def normalize_monic(num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> Tuple[List[sp.Expr], List[sp.Expr]]:
    den_lc = sp.nsimplify(den_desc[0])
    if den_lc == 0:
        raise ValueError("Denominator leading coefficient is zero.")
    num_desc = [sp.nsimplify(c/den_lc) for c in num_desc]
    den_desc = [sp.nsimplify(c/den_lc) for c in den_desc]
    return num_desc, den_desc

def ensure_proper(num_desc, den_desc) -> Tuple[List[sp.Expr], List[sp.Expr], sp.Expr, List[sp.Expr]]:
    s = sym_s()
    Pn = sp.Poly(sp.expand(sp.Poly(num_desc, s).as_expr()), s)
    Pd = sp.Poly(sp.expand(sp.Poly(den_desc, s).as_expr()), s)
    degN, degD = Pn.degree(), Pd.degree()
    if degN > degD:
        raise ValueError("Improper transfer function: deg(num) > deg(den). Not supported.")
    if degN == degD:
        q, r = sp.div(Pn, Pd)
        if q.degree() > 0:
            raise ValueError("Quasi-improper: division yields non-constant quotient.")
        Dfeed = sp.nsimplify(q.as_expr())
        R = sp.Poly(r.as_expr(), s)
        return R.all_coeffs(), den_desc, Dfeed, R.all_coeffs()
    return num_desc, den_desc, sp.nsimplify(0), num_desc

def coeffs_asc(desc: List[sp.Expr], n: int) -> List[sp.Expr]:
    asc = list(reversed(desc))
    if len(asc) < n:
        asc += [sp.nsimplify(0)] * (n - len(asc))
    elif len(asc) > n:
        asc = asc[:n]
    return [sp.nsimplify(c) for c in asc]

def square_free(poly: sp.Poly) -> bool:
    s = poly.gen
    return sp.gcd(poly, sp.Poly(sp.diff(poly.as_expr(), s), s)).degree() == 0

def tf_from_numden(num_desc, den_desc) -> sp.Expr:
    s = sym_s()
    Pn = sp.Poly(num_desc, s).as_expr()
    Pd = sp.Poly(den_desc, s).as_expr()
    return sp.together(sp.simplify(Pn / Pd))

def to_numeric(M, digits: int = 6):
    import numpy as np
    if isinstance(M, (sp.Expr, sp.Number)):
        return float(M.evalf(digits))
    if isinstance(M, sp.MatrixBase):
        return np.array(M.evalf(digits), dtype=float)
    if isinstance(M, (list, tuple)):
        return [to_numeric(x, digits) for x in M]
    return M

def pprint_matrix(M) -> str:
    return sp.pretty(sp.Matrix(M), use_unicode=True)
