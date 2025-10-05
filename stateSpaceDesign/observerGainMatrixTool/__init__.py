"""
stateSpaceDesign.observerGainMatrixTool
--------------------------------------
Object-oriented refactor of the standalone observer_gain_matrix.py utility.

Public entry points:
- CLI: `python -m stateSpaceDesign.observerGainMatrixTool.cli`
- Programmatic: `from stateSpaceDesign.observerGainMatrixTool.app import ObserverGainMatrixApp`
"""
__all__ = ["app", "apis", "cli", "core", "design", "io", "utils"]
