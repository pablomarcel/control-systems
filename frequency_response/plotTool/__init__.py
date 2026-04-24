"""frequency_response.plotTool — Object‑oriented frequency‑response workbench.

This package provides Bode / Nyquist / Nichols plotting for scalar TFs and
MIMO state‑space models with clean separation of concerns:
- utils: parsing, numerics, helpers
- core: metrics, Nichols grid, static constants
- design: model building (TF / SS → TF channels)
- tools: plotting backends (Matplotlib / Plotly)
- apis: high‑level service layer (facade) consumed by CLI and tests
- app: app container (in/out folders, logging)
- io: I/O helpers (saving, JSON report)
- cli: user‑facing command line interface

All public classes/methods are written for testability.
"""
__all__ = [
    "app", "apis", "core", "design", "io", "utils"
]
