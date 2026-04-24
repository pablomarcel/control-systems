from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import sympy as sp
from .utils import (
    sym_s, parse_poly, parse_tf_string, normalize_monic, ensure_proper, coeffs_asc,
    square_free, tf_from_numden, to_numeric, pprint_matrix
)

@dataclass
class Realization:
    A: sp.Matrix
    B: sp.Matrix
    C: sp.Matrix
    D: sp.Expr
    P: Optional[sp.Matrix] = None  # similarity matrix (e.g., Jordan)

    def as_dict(self) -> Dict:
        def m2s(M: sp.Matrix) -> List[List[str]]:
            return [[str(sp.nsimplify(M[i, j])) for j in range(M.shape[1])] for i in range(M.shape[0])]
        return {
            "A": m2s(self.A),
            "B": m2s(self.B),
            "C": m2s(self.C),
            "D": str(sp.nsimplify(self.D)),
            "P": None if self.P is None else m2s(self.P)
        }

@dataclass
class TransferFunctionSpec:
    num_desc: List[sp.Expr]
    den_desc: List[sp.Expr]

    @classmethod
    def from_tf_string(cls, tf: str) -> "TransferFunctionSpec":
        num, den = parse_tf_string(tf)
        return cls(num, den)

    @classmethod
    def from_num_den(cls, num: str, den: str) -> "TransferFunctionSpec":
        return cls(parse_poly(num), parse_poly(den))

@dataclass
class CanonicalFormCalculator:
    tf: TransferFunctionSpec
    numeric: bool = False
    digits: int = 6
    pretty: bool = False
    verify: bool = True

    # internal normalized data
    num_desc: List[sp.Expr] = field(init=False)
    den_desc: List[sp.Expr] = field(init=False)
    num_proper_desc: List[sp.Expr] = field(init=False)
    Dfeed: sp.Expr = field(init=False)
    _ref_A: sp.Matrix = field(init=False)
    _ref_B: sp.Matrix = field(init=False)
    _ref_C: sp.Matrix = field(init=False)
    _ref_D: sp.Expr = field(init=False)
    _target_tf: sp.Expr = field(init=False)

    def __post_init__(self):
        n, d = normalize_monic(self.tf.num_desc, self.tf.den_desc)
        self.num_desc, self.den_desc = n, d
        num_p, den_p, Dfeed, _ = ensure_proper(n, d)
        self.num_proper_desc, self.den_desc, self.Dfeed = num_p, den_p, Dfeed
        # reference realization
        Ac, Bc, Cc, Dd = self._controllable_companion()
        self._ref_A, self._ref_B, self._ref_C, self._ref_D = Ac, Bc, Cc, Dd
        self._target_tf = tf_from_numden(self.num_desc, self.den_desc)

    # --------- Canonical builders ---------
    def _controllable_companion(self) -> Tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Expr]:
        a_desc = self.den_desc
        n = len(a_desc) - 1
        if n <= 0:
            raise ValueError("Denominator must be at least first order.")
        a_asc = coeffs_asc(a_desc[1:], n)
        b_asc = coeffs_asc(self.num_proper_desc, n)
        A = sp.zeros(n)
        for i in range(n-1):
            A[i, i+1] = 1
        A[n-1, :] = sp.Matrix([[-ai for ai in a_asc]])
        B = sp.zeros(n, 1); B[n-1, 0] = 1
        C = sp.Matrix([b_asc])
        D = sp.nsimplify(self.Dfeed)
        return A, B, C, D

    def _observable_companion(self, Ac, Bc, Cc, Dd) -> Tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Expr]:
        Ao = Ac.T
        Bo = Cc.T
        Co = sp.Matrix([[0] * (Ao.shape[0] - 1) + [1]])
        return Ao, Bo, Co, Dd

    def _diagonal_pf(self) -> Optional[Tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Expr]]:
        s = sym_s()
        N = sp.Poly(self.num_proper_desc, s).as_expr()
        D = sp.Poly(self.den_desc, s)
        if not square_free(D):
            return None
        roots = list(sp.roots(D.as_expr()).items())
        poles = []
        for r, m in roots:
            if m != 1:
                return None
            poles.append(sp.nsimplify(r))

        def sort_key(z):
            zr = float(sp.re(z).evalf()); zi = float(sp.im(z).evalf())
            return (zr, zi)
        poles = sorted(poles, key=sort_key, reverse=True)

        Dprime = sp.diff(D.as_expr(), s)
        residues = [sp.nsimplify(sp.simplify(N.subs(s, p) / Dprime.subs(s, p))) for p in poles]

        Ad = sp.diag(*poles)
        Bd = sp.ones(len(poles), 1)
        Cd = sp.Matrix([residues])
        return Ad, Bd, Cd, sp.nsimplify(self.Dfeed)

    def _diagonal_eig(self, A, B, C, D):
        try:
            P, Ad = A.diagonalize(reals_only=False, sort=False)
            Pinv = P.inv()
            Bd = Pinv * B
            Cd = C * P
            return Ad, Bd, Cd, D
        except Exception:
            return None

    def _jordan(self, A, B, C, D):
        P, J = A.jordan_form()
        Pinv = P.inv()
        Bj = Pinv * B
        Cj = C * P
        return J, Bj, Cj, D, P

    # --------- Public API ---------
    def compute(self, which: str = "all") -> Dict[str, Realization]:
        results: Dict[str, Realization] = {}

        # Controllable
        if which in ("all", "controllable"):
            Ac, Bc, Cc, Dd = self._ref_A, self._ref_B, self._ref_C, self._ref_D
            if self.verify:
                Gc = self.tf_from_ss(Ac, Bc, Cc, Dd)
                assert sp.simplify(Gc - self._target_tf) == 0, "Controllable form failed verification."
            results["controllable"] = Realization(Ac, Bc, Cc, Dd)

        # Observable
        if which in ("all", "observable"):
            Ao, Bo, Co, Do = self._observable_companion(self._ref_A, self._ref_B, self._ref_C, self._ref_D)
            if self.verify:
                Go = self.tf_from_ss(Ao, Bo, Co, Do)
                assert sp.simplify(Go - self._target_tf) == 0, "Observable form failed verification."
            results["observable"] = Realization(Ao, Bo, Co, Do)

        # Diagonal
        if which in ("all", "diagonal"):
            diag_pf = self._diagonal_pf()
            if diag_pf is None:
                diag_eig = self._diagonal_eig(self._ref_A, self._ref_B, self._ref_C, self._ref_D)
                if diag_eig is not None:
                    Ad, Bd, Cd, Dd2 = diag_eig
                    if self.verify:
                        Gd = self.tf_from_ss(Ad, Bd, Cd, Dd2)
                        assert sp.simplify(Gd - self._target_tf) == 0, "Diagonal form failed verification."
                    results["diagonal"] = Realization(Ad, Bd, Cd, Dd2)
            else:
                Ad, Bd, Cd, Dd2 = diag_pf
                if self.verify:
                    Gd = self.tf_from_ss(Ad, Bd, Cd, Dd2)
                    assert sp.simplify(Gd - self._target_tf) == 0, "Diagonal form failed verification."
                results["diagonal"] = Realization(Ad, Bd, Cd, Dd2)

        # Jordan — compute only if explicitly requested or needed
        den_poly = sp.Poly(self.den_desc, sym_s())
        has_repeated = not square_free(den_poly)
        if which in ("jordan",) or (which == "all" and has_repeated):
            Aj, Bj, Cj, Dj, Pj = self._jordan(self._ref_A, self._ref_B, self._ref_C, self._ref_D)
            if self.verify:
                Gj = self.tf_from_ss(Aj, Bj, Cj, Dj)
                assert sp.simplify(Gj - self._target_tf) == 0, "Jordan form failed verification."
            results["jordan"] = Realization(Aj, Bj, Cj, Dj, P=Pj)

        return results

    # utilities
    @staticmethod
    def tf_from_ss(A: sp.Matrix, B: sp.Matrix, C: sp.Matrix, D: sp.Expr) -> sp.Expr:
        s = sym_s()
        I = sp.eye(A.shape[0])
        G = (C * (s * I - A).inv() * B)[0] + D
        return sp.together(sp.simplify(G))
