
# utils.py — common helpers (timing, logging decorator, pretty matrix)
from __future__ import annotations
import time
import functools
import logging
import numpy as np
import sympy as sp

def timing(fn):
    @functools.wraps(fn)
    def _wrap(*args, **kwargs):
        t0 = time.perf_counter()
        out = fn(*args, **kwargs)
        dt = time.perf_counter() - t0
        logging.getLogger(__name__).debug("%s took %.4fs", fn.__name__, dt)
        return out
    return _wrap

def pretty_matrix(M) -> str:
    return sp.pretty(sp.Matrix(M), use_unicode=True)

def to_numeric(M, digits: int = 8):
    if isinstance(M, sp.MatrixBase):
        return np.array(M.evalf(digits), dtype=float)
    return np.array(sp.Matrix(M).evalf(digits), dtype=float)

def sym_s() -> sp.Symbol:
    return sp.Symbol('s')

def sym_t() -> sp.Symbol:
    return sp.Symbol('t', real=True)

def to_expr_s(s_txt: str) -> sp.Expr:
    s_txt = s_txt.replace('^', '**').replace('X', 's').replace('x', 's').replace('S', 's')
    return sp.sympify(s_txt, locals={'s': sym_s()})

def to_expr_t(t_txt: str) -> sp.Expr:
    t_txt = t_txt.replace('^', '**')
    return sp.sympify(t_txt, locals={'t': sym_t()})

def is_square_free(poly: sp.Poly) -> bool:
    s = poly.gen
    return sp.gcd(poly, sp.Poly(sp.diff(poly.as_expr(), s), s)).degree() == 0
