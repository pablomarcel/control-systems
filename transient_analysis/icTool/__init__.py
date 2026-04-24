# ---------------------------------
# File: transient_analysis/icTool/__init__.py
# ---------------------------------
"""Response to initial conditions (Ogata §5-5) — icTool package.

Object-oriented, testable refactor of `initial_ic_lab.py`.

Public entry points:
- :mod:`transient_analysis.icTool.apis` for simple programmatic calls
- :mod:`transient_analysis.icTool.cli` for CLI (``python -m transient_analysis.icTool.cli``)
- :class:`transient_analysis.icTool.app.IcToolApp` for orchestration (in/out dirs)
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