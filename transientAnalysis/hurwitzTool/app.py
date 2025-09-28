from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
import sympy as sp

from .core import Polynomial, HurwitzMatrixBuilder, HurwitzMinors, HurwitzConditions, NumericChecker
from .utils import (
    parse_coeffs, parse_symbols_arg, detect_free_symbols,
    one_dim_interval_set, set_to_pretty_intervals,
)
from .io import IOManager


@dataclass(slots=True)
class HurwitzApp:
    """
    Application context for the Hurwitz stability tool.
    """
    base_dir: Path
    tol: float = 1e-10

    # declare fields for slots
    io: IOManager = field(init=False)
    num: NumericChecker = field(init=False)

    def __post_init__(self) -> None:
        self.io = IOManager(self.base_dir)
        self.num = NumericChecker(self.tol)

    # ---- Builders / Helpers ----
    def polynomial_from_str(self, coeffs: str) -> Polynomial:
        a = parse_coeffs(coeffs)
        return Polynomial(a)

    def detect_symbols(self, a: List[sp.Expr], symbols_arg: str | None, solvefor: str | None) -> List[sp.Symbol]:
        syms = parse_symbols_arg(symbols_arg) if symbols_arg else []
        if not syms:
            syms = detect_free_symbols(a)
        if solvefor:
            wanted = [sp.Symbol(s.strip()) for s in solvefor.split(',') if s.strip()]
            syms = wanted
        return syms

    # ---- Symbolic surface ----
    def hurwitz_matrix(self, poly: Polynomial) -> sp.Matrix:
        return HurwitzMatrixBuilder.matrix(poly.a_desc)

    def minors(self, poly: Polynomial) -> List[sp.Expr]:
        return HurwitzMinors.minors(poly.a_desc)

    def inequalities(self, poly: Polynomial, use_lienard: bool):
        return HurwitzConditions.inequalities(poly, use_lienard)

    def reduce_region(self, ineqs: List[sp.Rel], syms: List[sp.Symbol]) -> sp.Boolean | sp.Set:
        try:
            if len(syms) <= 1:
                return sp.reduce_inequalities(ineqs, syms[0] if syms else None)
            return sp.reduce_inequalities(ineqs, syms)
        except Exception:
            return sp.And(*ineqs)

    # ---- Numeric / scans ----
    def check_numeric(self, poly: Polynomial, subs: Dict[sp.Symbol, float], use_lienard: bool):
        return self.num.check(poly, subs, use_lienard)

    def scan1d(self, poly: Polynomial, sym: sp.Symbol, lo: float, hi: float, step: float, use_lienard: bool):
        return self.num.scan1d(poly, sym, lo, hi, step, use_lienard)

    def scan2d(self, poly: Polynomial, sx: sp.Symbol, xlo: float, xhi: float, dx: float,
               sy: sp.Symbol, ylo: float, yhi: float, dy: float, use_lienard: bool):
        return self.num.scan2d(poly, sx, xlo, xhi, dx, sy, ylo, yhi, dy, use_lienard)

    # ---- Interval pretty printer ----
    def pretty_intervals_1d(self, region: sp.Boolean | sp.Set, sym: sp.Symbol) -> tuple[str, str] | None:
        S = one_dim_interval_set(region, sym)
        if S is None:
            return None
        return set_to_pretty_intervals(S, latex=False), set_to_pretty_intervals(S, latex=True)
