# =============================
# File: transient_analysis/hurwitzTool/apis.py
# =============================
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import sympy as sp
import numpy as np

from .app import HurwitzApp
from .core import Polynomial


# ---- Requests / Results (TDD-friendly, serializable) ----
@dataclass(slots=True)
class NumericCheckRequest:
    coeffs: str
    subs: Dict[str, float]
    use_lienard: bool = False
    tol: float = 1e-10

@dataclass(slots=True)
class NumericCheckResult:
    ok: bool
    used: str
    a_numeric: List[float]
    minors_numeric: List[float]
    a0_pos: bool
    coeff_pos: bool


@dataclass(slots=True)
class SymbolicRegionRequest:
    coeffs: str
    symbols: Optional[str] = None
    solvefor: Optional[str] = None
    use_lienard: bool = False
    intervals_pretty: bool = False

@dataclass(slots=True)
class SymbolicRegionResult:
    variables: List[str]
    used: str
    region: str  # stringified SymPy object
    pretty: Optional[str] = None
    latex: Optional[str] = None


@dataclass(slots=True)
class Scan1DRequest:
    coeffs: str
    symbol: str
    lo: float
    hi: float
    step: float
    use_lienard: bool = False

@dataclass(slots=True)
class Scan1DResult:
    samples: List[Tuple[float, bool]]


@dataclass(slots=True)
class Scan2DRequest:
    coeffs: str
    sx: str
    sy: str
    xlo: float
    xhi: float
    dx: float
    ylo: float
    yhi: float
    dy: float
    use_lienard: bool = False

@dataclass(slots=True)
class Scan2DResult:
    xs: np.ndarray
    ys: np.ndarray
    Z: np.ndarray


class HurwitzService:
    def __init__(self, base_dir: Path) -> None:
        self.app = HurwitzApp(base_dir)

    # ---- Numeric ----
    def numeric_check(self, req: NumericCheckRequest) -> NumericCheckResult:
        poly = self.app.polynomial_from_str(req.coeffs)
        subs = {sp.Symbol(k): v for k, v in req.subs.items()}
        ok, detail = self.app.check_numeric(poly, subs, req.use_lienard)
        return NumericCheckResult(
            ok=ok,
            used=detail["used"],
            a_numeric=[float(x) for x in detail["a_numeric"]],
            minors_numeric=[float(x) for x in detail["Δ_numeric"]],
            a0_pos=bool(detail["a0>0"]),
            coeff_pos=bool(detail["coeff>0"]) ,
        )

    # ---- Symbolic ----
    def symbolic_region(self, req: SymbolicRegionRequest) -> SymbolicRegionResult:
        poly = self.app.polynomial_from_str(req.coeffs)
        syms = self.app.detect_symbols(poly.a_desc, req.symbols, req.solvefor)
        ineqs, used = self.app.inequalities(poly, req.use_lienard)
        region = self.app.reduce_region(ineqs, syms) if syms else sp.And(*ineqs)
        pretty = latex = None
        if req.intervals_pretty and len(syms) == 1:
            pi = self.app.pretty_intervals_1d(region, syms[0])
            if pi:
                pretty, latex = pi
        return SymbolicRegionResult(
            variables=[str(s) for s in syms],
            used=used,
            region=str(region),
            pretty=pretty,
            latex=latex,
        )

    # ---- Scans ----
    def scan1d(self, req: Scan1DRequest) -> Scan1DResult:
        poly = self.app.polynomial_from_str(req.coeffs)
        s = sp.Symbol(req.symbol)
        samples = self.app.scan1d(poly, s, req.lo, req.hi, req.step, req.use_lienard)
        return Scan1DResult(samples=samples)

    def scan2d(self, req: Scan2DRequest) -> Scan2DResult:
        poly = self.app.polynomial_from_str(req.coeffs)
        sx, sy = sp.Symbol(req.sx), sp.Symbol(req.sy)
        xs, ys, Z = self.app.scan2d(poly, sx, req.xlo, req.xhi, req.dx, sy, req.ylo, req.yhi, req.dy, req.use_lienard)
        return Scan2DResult(xs=xs, ys=ys, Z=Z)