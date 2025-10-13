
# utils.py
from __future__ import annotations
import numpy as np
import control as ct

def _is_statespace(obj) -> bool:
    try:
        return isinstance(obj, ct.StateSpace) or (hasattr(obj, "A") and hasattr(obj, "B"))
    except Exception:
        return False

def canonical_form_safe(sys, form: str):
    """
    Return (sys_cf, T, Ti) regardless of python-control's canonical_form signature.
    Accepts returns like: (T, Ti, sys_cf) | (sys_cf, T) | sys_cf
    """
    res = ct.canonical_form(sys, form=form)
    if not isinstance(res, tuple):
        res = (res,)
    if len(res) == 3:
        T, Ti, sys_cf = res
        return sys_cf, T, Ti
    if len(res) == 2:
        a, b = res
        if _is_statespace(a):
            sys_cf, T = a, b
        elif _is_statespace(b):
            T, sys_cf = a, b
        else:
            raise RuntimeError("Unexpected 2-tuple from canonical_form")
        Ti = np.linalg.inv(T)
        return sys_cf, T, Ti
    if len(res) == 1 and _is_statespace(res[0]):
        sys_cf = res[0]
        n = sys.A.shape[0]
        T = np.eye(n); Ti = np.eye(n)
        return sys_cf, T, Ti
    raise RuntimeError("Unexpected return from canonical_form")

def normalize_tf_coeffs(num, den):
    den = np.asarray(den, dtype=float).ravel()
    num = np.asarray(num, dtype=float).ravel()
    # strip leading zeros in den
    k = 0
    while k < len(den) and abs(den[k]) == 0:
        k += 1
    den = den[k:]
    if den.size == 0:
        raise ValueError("Invalid denominator (all zeros).")
    lead = den[0]
    den = den / lead
    num = num / lead
    if num.size < den.size:
        num = np.pad(num, (den.size - num.size, 0), mode="constant")
    return num, den

def tf_equal(sys1, sys2, tol: float = 1e-9) -> bool:
    g1 = ct.ss2tf(sys1)[0,0]
    g2 = ct.ss2tf(sys2)[0,0]
    n1 = np.squeeze(g1.num[0][0]); d1 = np.squeeze(g1.den[0][0])
    n2 = np.squeeze(g2.num[0][0]); d2 = np.squeeze(g2.den[0][0])
    n1, d1 = normalize_tf_coeffs(n1, d1)
    n2, d2 = normalize_tf_coeffs(n2, d2)
    return (np.allclose(n1, n2, atol=tol, rtol=0) and np.allclose(d1, d2, atol=tol, rtol=0))
