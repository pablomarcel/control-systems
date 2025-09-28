# ──────────────────────────────────────────────────────────────────────────────
# modernControl/transientAnalysis/hurwitzTool (OO refactor)
# Multi-file code presented inline. Copy files to matching paths.
# Python 3.10+ recommended.
# ──────────────────────────────────────────────────────────────────────────────

# =============================
# File: transientAnalysis/hurwitzTool/__init__.py
# =============================
from .app import HurwitzApp
from .apis import (
    NumericCheckRequest, NumericCheckResult,
    SymbolicRegionRequest, SymbolicRegionResult,
    Scan1DRequest, Scan1DResult,
    Scan2DRequest, Scan2DResult,
    HurwitzService,
)

__all__ = [
    "HurwitzApp",
    "NumericCheckRequest", "NumericCheckResult",
    "SymbolicRegionRequest", "SymbolicRegionResult",
    "Scan1DRequest", "Scan1DResult",
    "Scan2DRequest", "Scan2DResult",
    "HurwitzService",
]