
# core.py
from __future__ import annotations
import numpy as np
import control as ct
from scipy.linalg import schur
from .utils import canonical_form_safe

class CanonicalForms:
    """Pure compute engine for canonical conversions."""
    @staticmethod
    def ccf_from_tf(num, den):
        sys_tf = ct.TransferFunction(num, den)
        return ct.tf2ss(sys_tf)  # controllable companion

    @staticmethod
    def ocf_from_ss(sys):
        # try observable; else dual trick
        try:
            sys_obs, _, _ = canonical_form_safe(sys, form="observable")
            return sys_obs
        except Exception:
            A, B, C, D = sys.A, sys.B, sys.C, sys.D
            sys_dual = ct.ss(A.T, C.T, B.T, D.T)
            try:
                sys_dual_cf, _, _ = canonical_form_safe(sys_dual, form="reachable")
            except Exception:
                sys_dual_cf, _, _ = canonical_form_safe(sys_dual, form="controllable")
            A_o = sys_dual_cf.A.T
            B_o = sys_dual_cf.C.T
            C_o = sys_dual_cf.B.T
            D_o = sys_dual_cf.D.T
            return ct.ss(A_o, B_o, C_o, D_o)

    @staticmethod
    def modal_real(sys):
        # try modal; else real-Schur
        try:
            sys_mod, _, _ = canonical_form_safe(sys, form="modal")
            if np.isrealobj(sys_mod.A):
                return sys_mod
        except Exception:
            pass
        A, B, C, D = sys.A, sys.B, sys.C, sys.D
        Tschur, Q = schur(A, output="real")   # A = Q T Q^T
        A_m = Tschur
        B_m = Q.T @ B
        C_m = C @ Q
        return ct.ss(A_m, B_m, C_m, D)
