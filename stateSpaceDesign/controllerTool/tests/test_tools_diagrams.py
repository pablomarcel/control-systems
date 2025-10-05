# -*- coding: utf-8 -*-
from stateSpaceDesign.controllerTool.tools.diagrams import mermaid_class_diagram

def test_mermaid_diagram_nonempty():
    s = mermaid_class_diagram()
    assert "classDiagram" in s and "ControllerToolApp" in s
