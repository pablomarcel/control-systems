from __future__ import annotations
from typing import List, Optional, Dict, Callable
import sympy as sp
from .utils import sym_s, sym_t, parse_tf_string, parse_poly, normalize_monic, ensure_proper, coeffs_asc, square_free

# --------- Canonical Realization Registry (Strategy pattern) ---------

_CANONICAL_BUILDERS: Dict[str, Callable[[List[sp.Expr], List[sp.Expr]], sp.Matrix]] = {}

def register_canonical(name: str):
    def deco(fn: Callable[[List[sp.Expr], List[sp.Expr]], sp.Matrix]):
        _CANONICAL_BUILDERS[name] = fn
        return fn
    return deco

def get_canonical_names() -> List[str]:
    return list(_CANONICAL_BUILDERS.keys())

# ------------------------- Realization helpers -------------------------

def controllable_A(num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> sp.Matrix:
    a_desc = den_desc
    n = len(a_desc) - 1
    if n <= 0:
        raise ValueError("Denominator must be at least first order.")
    a_asc = coeffs_asc(a_desc[1:], n)
    A = sp.zeros(n)
    for i in range(n - 1):
        A[i, i + 1] = 1
    A[n - 1, :] = sp.Matrix([[-ai for ai in a_asc]])
    return A

def observable_A_from(Ac: sp.Matrix) -> sp.Matrix:
    return Ac.T

def diagonal_A_pf(den_desc: List[sp.Expr]) -> Optional[sp.Matrix]:
    s = sym_s()
    D = sp.Poly(den_desc, s)
    if not square_free(D):
        return None
    roots = list(sp.roots(D.as_expr()).keys())
    def sort_key(z):
        return (float(sp.re(z).evalf()), float(sp.im(z).evalf()))
    poles = sorted((sp.nsimplify(r) for r in roots), key=sort_key, reverse=True)
    return sp.diag(*poles)

def jordan_form(A: sp.Matrix):
    P, J = A.jordan_form()
    return J, P

# Register strategies
@register_canonical("controllable")
def _build_controllable(num_desc, den_desc):
    return controllable_A(num_desc, den_desc)

@register_canonical("observable")
def _build_observable(num_desc, den_desc):
    return observable_A_from(controllable_A(num_desc, den_desc))

@register_canonical("diagonal")
def _build_diagonal(num_desc, den_desc):
    Ad = diagonal_A_pf(den_desc)
    if Ad is not None:
        return Ad
    # fallback to eigen diagonalization if possible; else controllable
    Ac = controllable_A(num_desc, den_desc)
    try:
        P, Ad2 = Ac.diagonalize(reals_only=False, sort=False)
        return Ad2
    except Exception:
        return Ac

@register_canonical("jordan")
def _build_jordan(num_desc, den_desc):
    Ac = controllable_A(num_desc, den_desc)
    J, _ = Ac.jordan_form()
    return J

# ------------------------- Engine -------------------------

class StateTransitionEngine:
    """Compute Φ(t)=e^{At} given a TF and a canonical realization choice."""
    def __init__(self, canonical: str = "controllable"):
        if canonical not in _CANONICAL_BUILDERS:
            raise ValueError(f"Unknown canonical '{canonical}'. Available: {get_canonical_names()}")
        self.canonical = canonical

    def parse_inputs(self, tf: str | None, num: str | None, den: str | None, example: str | None):
        if example == "ogata_9_1":
            num_desc, den_desc = parse_tf_string("(s+3)/(s^2+3*s+2)")
        else:
            if tf:
                num_desc, den_desc = parse_tf_string(tf)
            else:
                if not (num and den):
                    raise ValueError("Provide `tf` OR both `num` and `den`.")
                num_desc = parse_poly(num)
                den_desc = parse_poly(den)
        num_desc, den_desc = normalize_monic(num_desc, den_desc)
        num_desc, den_desc, _ = ensure_proper(num_desc, den_desc)
        return num_desc, den_desc

    def build_A(self, num_desc: List[sp.Expr], den_desc: List[sp.Expr]) -> sp.Matrix:
        A = _CANONICAL_BUILDERS[self.canonical](num_desc, den_desc)
        return A

    def phi_symbolic(self, A: sp.Matrix) -> sp.Matrix:
        t = sym_t()
        return (A * t).exp()

    def phi_inverse_symbolic(self, A: sp.Matrix) -> sp.Matrix:
        t = sym_t()
        return (-A * t).exp()
