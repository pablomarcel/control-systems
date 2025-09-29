# ---------------------------------
# File: transientAnalysis/icTool/__init__.py
# ---------------------------------
"""Response to initial conditions (Ogata §5-5) — icTool package.

Object-oriented, testable refactor of `initial_ic_lab.py`.

Public entry points:
- :mod:`transientAnalysis.icTool.apis` for simple programmatic calls
- :mod:`transientAnalysis.icTool.cli` for CLI (``python -m transientAnalysis.icTool.cli``)
- :class:`transientAnalysis.icTool.app.IcToolApp` for orchestration (in/out dirs)
"""
from .core import ICProblem, ICSolver, CompareResult, CaseResult
from .app import IcToolApp

__all__ = [
    "ICProblem",
    "ICSolver",
    "CompareResult",
    "CaseResult",
    "IcToolApp",
]