# transientAnalysis/routhTool/core.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Sequence, Union, Tuple

Number = Union[float, int]

try:
    import sympy as sp
except Exception:  # pragma: no cover
    sp = None  # symbolic disabled

@dataclass(slots=True)
class RouthConfig:
    """Config knobs for Routh builder."""
    eps: float = 1e-9

@dataclass(slots=True)
class RouthResult:
    """Container for results of building a Routh array."""
    array: List[List[Union[Number, "sp.Basic"]]]
    first_column: List[Union[Number, "sp.Basic"]]
    degrees: List[int]
    rhp_by_routh: Optional[int] = None
    rhp_by_roots: Optional[int] = None  # numeric verification if computed
    hurwitz_minors: Optional[List["sp.Basic"]] = None
    stability_condition: Optional[object] = None  # SymPy Boolean or None

def _is_zero(x, tol=1e-12):
    if sp and isinstance(x, sp.Basic):
        return sp.simplify(x) == 0
    try:
        return abs(float(x)) < tol
    except Exception:
        return False

def _sign_of(x, tol=1e-12):
    if sp and isinstance(x, sp.Basic):
        return None
    val = float(x)
    if abs(val) < tol:
        return 0
    return 1 if val > 0 else -1

class RouthArrayBuilder:
    """
    Build Routh arrays numerically or symbolically.
    - ε-trick for zero leading element in a row.
    - Auxiliary polynomial when an entire row becomes zero.
    - Optional: Hurwitz minors (SymPy), inequality solving for 1 symbol, numeric verification.

    The class is stateless and thus easy to test; config is injected via RouthConfig.
    """

    def __init__(self, config: Optional[RouthConfig] = None):
        self.cfg = config or RouthConfig()

    # ---------- Core algorithm ----------

    def build_array(
        self,
        coeffs: Sequence[Union[Number, "sp.Basic"]],
    ) -> Tuple[List[List[Union[Number, "sp.Basic"]]], List[Union[Number, "sp.Basic"]], List[int]]:
        use_sympy = sp is not None and any(isinstance(c, sp.Basic) for c in coeffs)
        n = len(coeffs) - 1
        width = (n + 2) // 2
        A = [[0 for _ in range(width)] for _ in range(n + 1)]
        degrees = [n - i for i in range(n + 1)]

        # first two rows
        ei = 0
        oi = 1
        for j in range(width):
            A[0][j] = coeffs[ei] if ei <= n else 0
            ei += 2
        for j in range(width):
            A[1][j] = coeffs[oi] if oi <= n else 0
            oi += 2

        eps_sym = sp.Symbol("epsilon", positive=True) if (use_sympy) else None

        for i in range(2, n + 1):
            upper = A[i - 2]
            lower = A[i - 1]

            # entire row of zeros -> auxiliary poly derivative
            if all(_is_zero(x) for x in lower):
                m = degrees[i - 1]
                new_row = []
                for j, cj in enumerate(upper):
                    exp = m - 2 * j
                    new_row.append(cj * exp if exp > 0 else 0)
                A[i] = (new_row + [0] * width)[:width]
                continue
            # leading element zero? ε-trick
            if _is_zero(lower[0]):
                A[i - 1][0] = eps_sym if (eps_sym is not None) else self.cfg.eps

            # compute row i
            denom = A[i - 1][0]
            row = []
            for j in range(width - 1):
                num = lower[0] * upper[j + 1] - upper[0] * lower[j + 1]
                row.append(num / denom)
            row.append(0)
            A[i] = row

            # numerical annihilation -> auxiliary
            if all(_is_zero(x) for x in A[i]):
                m = degrees[i - 1]
                new_row = []
                for j, cj in enumerate(upper):
                    exp = m - 2 * j
                    new_row.append(cj * exp if exp > 0 else 0)
                A[i] = (new_row + [0] * width)[:width]

        first_col = [A[i][0] for i in range(n + 1)]
        return A, first_col, degrees

    # ---------- Derived quantities ----------

    def sign_changes_first_column(
        self, first_col: Sequence[Union[Number, "sp.Basic"]]
    ) -> Optional[int]:
        if any(sp and isinstance(x, sp.Basic) for x in first_col):
            return None
        signs = [_sign_of(x) for x in first_col]
        signs = [s for s in signs if s != 0]
        changes = 0
        for a, b in zip(signs, signs[1:]):
            if a * b < 0:
                changes += 1
        return changes

    def verify_with_roots(self, coeffs: Sequence[Union[Number, "sp.Basic"]]) -> Optional[int]:
        try:
            import numpy as np
        except Exception:  # pragma: no cover
            return None
        if any(sp and isinstance(c, sp.Basic) for c in coeffs):
            return None
        c = [float(c_) for c_ in coeffs]
        r = np.roots(c)
        return int((r.real > 0).sum())

    def hurwitz_minors(self, coeffs: Sequence[Union[Number, "sp.Basic"]]) -> List["sp.Basic"]:
        if sp is None:
            raise RuntimeError("Hurwitz minors require SymPy. Please install sympy.")
        n = len(coeffs) - 1
        H = sp.zeros(n)
        # classic Hurwitz matrix construction
        for i in range(n):
            for j in range(n):
                idx = 2 * j - i
                H[i, j] = 0 if idx < 0 else (coeffs[idx] if idx <= n else 0)
        minors = []
        for k in range(1, n + 1):
            minors.append(sp.simplify(H[:k, :k].det()))
        return minors

    def stability_region_for(self, first_col: Sequence[Union[Number, "sp.Basic"]], symbol_name: str):
        if sp is None:
            raise RuntimeError("SymPy not available; cannot solve symbolically.")
        sym = sp.Symbol(symbol_name, real=True)
        cond = sp.S.true
        for expr in first_col:
            if isinstance(expr, (float, int)):
                if float(expr) <= 0:
                    return sp.S.false
                continue
            cond = sp.And(cond, sp.StrictGreaterThan(sp.simplify(expr), 0))
        try:
            cond = sp.reduce_inequalities(cond, [sym])
        except Exception:
            pass
        return cond

    # ---------- One-shot orchestrator ----------

    def run(
        self,
        coeffs: Sequence[Union[Number, "sp.Basic"]],
        *,
        symbol_to_solve: Optional[str] = None,
        compute_hurwitz: bool = False,
        verify_numeric: bool = False,
    ) -> RouthResult:
        A, fc, degs = self.build_array(coeffs)
        rhp_r = self.sign_changes_first_column(fc)
        rhp_v = self.verify_with_roots(coeffs) if verify_numeric else None
        minors = self.hurwitz_minors(coeffs) if compute_hurwitz else None
        cond = self.stability_region_for(fc, symbol_to_solve) if symbol_to_solve else None
        return RouthResult(
            array=A,
            first_column=list(fc),
            degrees=list(degs),
            rhp_by_routh=rhp_r,
            rhp_by_roots=rhp_v,
            hurwitz_minors=minors,
            stability_condition=cond,
        )