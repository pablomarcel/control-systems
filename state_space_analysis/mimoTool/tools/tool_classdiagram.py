"""
Lightweight class-diagram generator using graphviz if available.
Gracefully degrades when Graphviz executables (e.g., `dot`) are missing.
"""
from __future__ import annotations
from typing import Optional

try:
    from graphviz import Digraph  # optional python package
    from graphviz.backend.execute import ExecutableNotFound
except Exception:  # pragma: no cover
    Digraph = None  # type: ignore
    ExecutableNotFound = Exception  # type: ignore

def emit_basic_diagram(out_path: str = "state_space_analysis/mimoTool/out/mimo_classes") -> Optional[str]:
    """Render a minimal class diagram.
    Returns the rendered file path when successful, or None if Graphviz
    (python package or the `dot` executable) is not available.
    """
    if Digraph is None:
        return None
    g = Digraph("mimo_tool", format="png")
    g.attr(rankdir="LR")
    g.node("MIMOSystem", "MIMOSystem\n(core.MIMOSystem)")
    g.node("PlantFactory", "PlantFactory\n(design.PlantFactory)")
    g.node("MIMOToolApp", "MIMOToolApp\n(app.MIMOToolApp)")
    g.edges([("PlantFactory","MIMOSystem"), ("MIMOToolApp","MIMOSystem")])
    try:
        return g.render(out_path, cleanup=True)
    except ExecutableNotFound:
        # dot not installed / not on PATH → degrade quietly
        return None
