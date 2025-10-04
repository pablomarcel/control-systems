
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import control as ct
from typing import Tuple
from .tools.trace_uml import track

def _is_statespace(obj) -> bool:
    try:
        return isinstance(obj, ct.StateSpace) or (hasattr(obj, "A") and hasattr(obj, "B"))
    except Exception:
        return False

@dataclass(slots=True)
class CanonicalFormsEngine:
    @staticmethod
    @track("CanonicalFormsEngine.canonical_form_safe", "control.canonical_form")
    def canonical_form_safe(sys: ct.StateSpace, form: str):
        # Return (sys_cf, T, Ti) regardless of python-control's canonical_form signature.
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

    @staticmethod
    @track("CanonicalFormsEngine.normalize_tf_coeffs", "numpy.pad")
    def normalize_tf_coeffs(num, den):
        den = np.asarray(den, dtype=float).ravel()
        num = np.asarray(num, dtype=float).ravel()
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

    @staticmethod
    @track("CanonicalFormsEngine.make_ccf_from_tf", "control.tf2ss")
    def make_ccf_from_tf(num, den) -> ct.StateSpace:
        sys_tf = ct.TransferFunction(num, den)
        return ct.tf2ss(sys_tf)

    @staticmethod
    @track("CanonicalFormsEngine.make_ocf_from_ss", "control.canonical_form")
    def make_ocf_from_ss(sys: ct.StateSpace) -> ct.StateSpace:
        try:
            sys_obs, _, _ = CanonicalFormsEngine.canonical_form_safe(sys, form='observable')
            return sys_obs
        except Exception:
            A, B, C, D = sys.A, sys.B, sys.C, sys.D
            sys_dual = ct.ss(A.T, C.T, B.T, D.T)
            try:
                sys_dual_cf, _, _ = CanonicalFormsEngine.canonical_form_safe(sys_dual, form='reachable')
            except Exception:
                sys_dual_cf, _, _ = CanonicalFormsEngine.canonical_form_safe(sys_dual, form='controllable')
            A_o = sys_dual_cf.A.T
            B_o = sys_dual_cf.C.T
            C_o = sys_dual_cf.B.T
            D_o = sys_dual_cf.D.T
            return ct.ss(A_o, B_o, C_o, D_o)

    @staticmethod
    @track("CanonicalFormsEngine.make_modal_real", "scipy.linalg.schur")
    def make_modal_real(sys: ct.StateSpace) -> ct.StateSpace:
        try:
            sys_mod, _, _ = CanonicalFormsEngine.canonical_form_safe(sys, form='modal')
            if np.isrealobj(sys_mod.A):
                return sys_mod
        except Exception:
            pass
        from scipy.linalg import schur
        A, B, C, D = sys.A, sys.B, sys.C, sys.D
        Tschur, Q = schur(A, output='real')
        A_m = Tschur
        B_m = Q.T @ B
        C_m = C @ Q
        return ct.ss(A_m, B_m, C_m, D)

    @staticmethod
    @track("CanonicalFormsEngine.tf_equal", "control.ss2tf")
    def tf_equal(sys1: ct.StateSpace, sys2: ct.StateSpace, tol: float = 1e-9) -> bool:
        g1 = ct.ss2tf(sys1)[0,0]
        g2 = ct.ss2tf(sys2)[0,0]
        n1 = np.squeeze(g1.num[0][0]); d1 = np.squeeze(g1.den[0][0])
        n2 = np.squeeze(g2.num[0][0]); d2 = np.squeeze(g2.den[0][0])
        n1, d1 = CanonicalFormsEngine.normalize_tf_coeffs(n1, d1)
        n2, d2 = CanonicalFormsEngine.normalize_tf_coeffs(n2, d2)
        return (np.allclose(n1, n2, atol=tol, rtol=0) and np.allclose(d1, d2, atol=tol, rtol=0))

    @staticmethod
    @track("CanonicalFormsEngine.symbolic_G", "sympy.simplify")
    def symbolic_G(sys: ct.StateSpace):
        try:
            import sympy as sp
            s = sp.symbols('s')
            A, B, C, D = sys.A, sys.B, sys.C, sys.D
            As, Bs, Cs, Ds = sp.Matrix(A), sp.Matrix(B), sp.Matrix(C), sp.Matrix(D)
            Gs = sp.simplify(Cs * (s*sp.eye(As.shape[0]) - As)**-1 * Bs + Ds)
            return sp.simplify(Gs[0,0])
        except Exception:
            return None
