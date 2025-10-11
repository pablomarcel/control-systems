
from __future__ import annotations
import importlib.util

from transientAnalysis.routhTool.tools import diagram, logging_tools
from transientAnalysis.routhTool import core, app, apis
from transientAnalysis.routhTool.design import PRESETS

def test_presets_present():
    # Basic sanity on design presets
    names = {p.name for p in PRESETS}
    assert {"cubic_numeric","cubic_gain","quartic_gain","row_of_zeros_demo"} <= names

def test_diagram_emitters():
    plant = diagram.emit_plantuml([core, app, apis])
    mer = diagram.emit_mermaid([core, app, apis])
    assert "@startuml" in plant and "@enduml" in plant
    assert "classDiagram" in mer

def test_logging_tools_trace_decorator(capsys):
    calls = {}
    @logging_tools.trace
    def f(x):
        calls["seen"] = x
        return x * 2

    out = f(3)
    assert calls["seen"] == 3
    assert out == 6
