
from __future__ import annotations
from state_space_analysis.stateTool.tools.decorators import traced
from state_space_analysis.stateTool.tools.uml_tools import plantuml_skeleton

def test_traced_decorator():
    @traced
    def f(x): return x+1
    assert f(2) == 3

def test_uml_skeleton_has_markers():
    txt = plantuml_skeleton()
    assert "@startuml" in txt and "StateToolApp" in txt and "@enduml" in txt
