from __future__ import annotations
import sympy as sp
import numpy as np

def safe_nsimplify(expr):
    try:
        return sp.nsimplify(expr, rational=True)
    except TypeError:
        return sp.nsimplify(expr)
    except Exception:
        return sp.simplify(expr)

def monic_fraction(expr, s: sp.Symbol):
    expr = sp.together(sp.simplify(expr))
    num, den = sp.fraction(expr)
    num = safe_nsimplify(num); den = safe_nsimplify(den)
    try:
        den_poly = sp.Poly(den, s)
        lc = den_poly.LC()
        if lc != 1:
            expr = sp.simplify((num/lc)/(den/lc))
            num, den = sp.fraction(expr)
        expr = sp.cancel(num/den); num, den = sp.fraction(expr)
        return sp.expand(num), sp.expand(den)
    except Exception:
        return sp.expand(num), sp.expand(den)

def symbolic_G(A, B, C, D):
    s = sp.symbols('s')
    As, Bs, Cs, Ds = sp.Matrix(A), sp.Matrix(B), sp.Matrix(C), sp.Matrix(D)
    Gs = sp.simplify(Cs * (s*sp.eye(As.shape[0]) - As)**-1 * Bs + Ds)
    return Gs, s

def charpoly_monic(A):
    s = sp.symbols('s')
    As = sp.Matrix(A)
    char = sp.factor(sp.det(s*sp.eye(As.shape[0]) - As))
    return sp.Poly(char, s).monic().as_expr()
