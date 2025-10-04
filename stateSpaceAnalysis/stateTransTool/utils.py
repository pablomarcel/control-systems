from __future__ import annotations
from typing import List, Tuple
import numpy as np
import sympy as sp

def sym_s() -> sp.Symbol:
    return sp.Symbol('s')

def sym_t() -> sp.Symbol:
    return sp.Symbol('t', real=True)

def to_expr(text: str) -> sp.Expr:
    txt = text.replace('^', '**').replace('X', 's').replace('x', 's').replace('S', 's')
    return sp.sympify(txt, locals={'s': sym_s()})

def parse_poly(arg) -> List[sp.Expr]:
    if isinstance(arg, (list, tuple)):
        return [sp.nsimplify(v) for v in arg]
    txt = str(arg).strip()
    if any(ch in txt for ch in ('s', 'S', 'x', 'X', '+', '-', '*', '/', '(', ')', '^')):
        poly = sp.Poly(sp.expand(to_expr(txt)), sym_s())
        return [sp.nsimplify(c) for c in poly.all_coeffs()]
    parts = [p for p in txt.replace(';', ',').split(',') if p.strip() != '']
    return [sp.nsimplify(p) for p in parts]

def parse_tf_string(tf_str: str) -> Tuple[List[sp.Expr], List[sp.Expr]]:
    expr = sp.together(to_expr(tf_str))
    num, den = sp.fraction(expr)
    Ps = sp.Poly(sp.expand(num), sym_s())
    Qs = sp.Poly(sp.expand(den), sym_s())
    return [sp.nsimplify(c) for c in Ps.all_coeffs()], [sp.nsimplify(c) for c in Qs.all_coeffs()]

def normalize_monic(num_desc: List[sp.Expr], den_desc: List[sp.Expr]):
    den_lc = sp.nsimplify(den_desc[0])
    if den_lc == 0:
        raise ValueError("Denominator leading coefficient is zero.")
    num_desc = [sp.nsimplify(c / den_lc) for c in num_desc]
    den_desc = [sp.nsimplify(c / den_lc) for c in den_desc]
    return num_desc, den_desc

def ensure_proper(num_desc: List[sp.Expr], den_desc: List[sp.Expr]):
    s = sym_s()
    Pn = sp.Poly(sp.expand(sp.Poly(num_desc, s).as_expr()), s)
    Pd = sp.Poly(sp.expand(sp.Poly(den_desc, s).as_expr()), s)
    degN, degD = Pn.degree(), Pd.degree()
    if degN > degD:
        raise ValueError("Improper transfer function (deg num > deg den).")
    if degN == degD:
        q, r = sp.div(Pn, Pd)
        if q.degree() > 0:
            raise ValueError("Quotient is not constant (would need derivative-of-input).")
        Dfeed = sp.nsimplify(q.as_expr())
        num_desc = sp.Poly(r.as_expr(), s).all_coeffs()
        return num_desc, den_desc, Dfeed
    return num_desc, den_desc, sp.Integer(0)

def coeffs_asc(desc: List[sp.Expr], n: int) -> List[sp.Expr]:
    asc = list(reversed(desc))
    if len(asc) < n:
        asc += [sp.Integer(0)] * (n - len(asc))
    elif len(asc) > n:
        asc = asc[:n]
    return [sp.nsimplify(c) for c in asc]

def square_free(poly: sp.Poly) -> bool:
    s = poly.gen
    return sp.gcd(poly, sp.Poly(sp.diff(poly.as_expr(), s), s)).degree() == 0

def pretty_matrix(M) -> str:
    return sp.pretty(sp.Matrix(M), use_unicode=True)

def to_numeric(M, digits: int = 8):
    if isinstance(M, sp.MatrixBase):
        return np.array(M.evalf(digits), dtype=float)
    return np.array(sp.Matrix(M).evalf(digits), dtype=float)
