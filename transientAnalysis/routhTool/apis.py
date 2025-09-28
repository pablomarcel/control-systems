# transientAnalysis/routhTool/apis.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any

from .core import RouthArrayBuilder, RouthConfig, RouthResult
from .utils import parse_coeffs, coerce_tokens

@dataclass(slots=True)
class RouthRequest:
    """Programmatic request payload."""
    coeffs: str  # e.g. "1, 5, 6, K"
    symbols: Optional[List[str]] = None
    solve_for: Optional[str] = None
    eps: float = 1e-9
    compute_hurwitz: bool = False
    verify_numeric: bool = False

@dataclass(slots=True)
class RouthResponse:
    """Programmatic response payload (JSON-safe-ish)."""
    array: List[List[str]]
    first_column: List[str]
    degrees: List[int]
    rhp_by_routh: Optional[int]
    rhp_by_roots: Optional[int]
    hurwitz_minors: Optional[List[str]]
    stability_condition: Optional[str]

def _stringify_result(res: RouthResult) -> RouthResponse:
    from .utils import fmt_cell
    arr = [[fmt_cell(x) for x in row] for row in res.array]
    fc = [fmt_cell(x) for x in res.first_column]
    minors = [str(m) for m in (res.hurwitz_minors or [])] if res.hurwitz_minors else None
    cond = str(res.stability_condition) if res.stability_condition is not None else None
    return RouthResponse(
        array=arr,
        first_column=fc,
        degrees=res.degrees,
        rhp_by_routh=res.rhp_by_routh,
        rhp_by_roots=res.rhp_by_roots,
        hurwitz_minors=minors,
        stability_condition=cond,
    )

def array_api(req: RouthRequest) -> RouthResponse:
    tokens = parse_coeffs(req.coeffs)
    coeffs = coerce_tokens(tokens, req.symbols or [])
    builder = RouthArrayBuilder(RouthConfig(eps=req.eps))
    result = builder.run(
        coeffs,
        symbol_to_solve=req.solve_for,
        compute_hurwitz=req.compute_hurwitz,
        verify_numeric=req.verify_numeric,
    )
    return _stringify_result(result)

# Convenience focused endpoint for “solve for K”
def solve_api(coeffs: str, symbol: str, *, eps: float = 1e-9) -> RouthResponse:
    req = RouthRequest(coeffs=coeffs, symbols=[symbol], solve_for=symbol, eps=eps)
    return array_api(req)