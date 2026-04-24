from __future__ import annotations
def safe_nsimplify(expr):
    import sympy as sp
    try:
        return sp.nsimplify(expr, rational=True, tolerance=1e-12)
    except TypeError:
        return sp.nsimplify(expr, rational=True)
