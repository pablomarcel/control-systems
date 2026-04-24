from __future__ import annotations
import importlib

def test_import_tool_plantuml():
    mod = importlib.import_module("transient_analysis.hurwitzTool.tools.tool_plantuml")
    assert hasattr(mod, "__name__")
