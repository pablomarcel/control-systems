
from __future__ import annotations
from frequency_response.bodeTool.tools.diagram import emit_puml

def test_emit_puml_has_classes_and_relations():
    txt = emit_puml()
    assert "@startuml" in txt and "@enduml" in txt
    assert "BodeApp" in txt and "Analyzer" in txt and "BodePlotter" in txt
