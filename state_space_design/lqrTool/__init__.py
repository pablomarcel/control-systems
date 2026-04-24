"""state_space_design.lqrTool — Object-oriented LQR design + simulations.

This package refactors the original monolithic `lqr.py` into testable,
extensible modules with a clean CLI entry point.

Submodules:
- core: state-space model + response containers
- design: LQR design + prefilters
- io: parsing helpers and I/O glue
- utils: small utilities (controllability rank, decorators)
- apis: request/response dataclasses
- app: orchestration layer
- cli: argparse-based CLI entry
- tools: aux scripts (class diagram export, etc.)
"""

__all__ = [
    "core", "design", "io", "utils", "apis", "app"
]
