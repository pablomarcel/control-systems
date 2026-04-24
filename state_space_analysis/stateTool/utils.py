from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import sympy as sp

def sym_s() -> sp.Symbol:
    return sp.Symbol("s")

def to_expr_s(s_txt: str) -> sp.Expr:
    s_txt = s_txt.replace("^", "**").replace("X", "s").replace("x", "s").replace("S", "s")
    return sp.sympify(s_txt, locals={"s": sym_s()})

def strip_outer_parens(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(s)-1:
                    return s
        return s[1:-1].strip()
    return s

def parse_matrix(txt: str) -> sp.Matrix:
    txt = txt.strip()
    if txt.startswith("["):
        return sp.Matrix(sp.sympify(txt))
    rows = [r for r in txt.split(";") if r.strip()]
    mat = []
    for r in rows:
        cols = [c for c in r.replace(",", " ").split() if c.strip()]
        mat.append([sp.nsimplify(c) for c in cols])
    return sp.Matrix(mat)

def split_fraction_raw(tf_str: str) -> Optional[Tuple[str, str]]:
    s = tf_str.strip()
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "/" and depth == 0:
            return s[:i].strip(), s[i+1:].strip()
    return None

def parse_poly_text(txt: str) -> List[sp.Expr]:
    txt = strip_outer_parens(txt)
    poly = sp.Poly(sp.expand(to_expr_s(txt)), sym_s())
    return [sp.nsimplify(c) for c in poly.all_coeffs()]

def parse_poly(arg: str | List[float]) -> List[sp.Expr]:
    if isinstance(arg, (list, tuple)):
        return [sp.nsimplify(v) for v in arg]
    txt = str(arg).strip()
    if any(ch in txt for ch in ("s","S","x","X","+","-","*","/","(",")","^")):
        poly = sp.Poly(sp.expand(to_expr_s(txt)), sym_s())
        return [sp.nsimplify(c) for c in poly.all_coeffs()]
    parts = [p for p in txt.replace(";", ",").split(",") if p.strip()]
    return [sp.nsimplify(p) for p in parts]

def normalize_monic(num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> Tuple[List[sp.Expr], List[sp.Expr]]:
    lc = sp.nsimplify(den_desc[0])
    if lc == 0:
        raise ValueError("Denominator leading coefficient is zero.")
    return [sp.nsimplify(c/lc) for c in num_desc], [sp.nsimplify(c/lc) for c in den_desc]

def ensure_proper(num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> Tuple[List[sp.Expr], List[sp.Expr], sp.Expr]:
    s = sym_s()
    Pn = sp.Poly(sp.expand(sp.Poly(num_desc, s).as_expr()), s)
    Pd = sp.Poly(sp.expand(sp.Poly(den_desc, s).as_expr()), s)
    if Pn.degree() > Pd.degree():
        raise ValueError("Improper TF: deg(num) > deg(den).")
    if Pn.degree() == Pd.degree():
        q, r = sp.div(Pn, Pd)
        if q.degree() > 0:
            raise ValueError("Quasi-improper TF: non-constant quotient.")
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

def pretty(M: sp.Matrix) -> str:
    return sp.pretty(M, use_unicode=True)

def to_numeric(M: sp.Matrix, digits: int = 8):
    return np.array(M.evalf(digits), dtype=float)
