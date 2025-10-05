#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
class_diagram.py — simple class diagram generator using graphviz (if available).
This is optional; if graphviz isn't installed, it will print a friendly message.
"""

from __future__ import annotations
import os

def generate_class_diagram(out_path: str = "stateSpaceDesign/regulatorTool/out/regulatorTool_classes.dot") -> str:
    try:
        from graphviz import Digraph
    except Exception:
        print("Graphviz not installed; skipping class diagram generation.")
        return ""
    g = Digraph("regulatorTool", format="png")
    g.attr(rankdir="LR", splines="ortho", nodesep="0.4", ranksep="0.4")
    # Nodes
    g.node("PlantFactory", shape="record", label="{PlantFactory|+ from_tf()}")
    g.node("RegulatorDesigner", shape="record", label="{RegulatorDesigner|+ run()\\l+ simulate_initial()\\l+ bode_open_closed()\\l+ root_locus()}")
    g.node("RegulatorService", shape="record", label="{RegulatorService|+ run()}")
    g.node("RegulatorRunRequest", shape="record", label="{RegulatorRunRequest| fields... }")
    g.edge("PlantFactory", "RegulatorDesigner")
    g.edge("RegulatorRunRequest", "RegulatorService")
    g.edge("RegulatorService", "RegulatorDesigner")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    g.render(out_path, cleanup=True)
    print(f"Class diagram written to {out_path}.png")
    return out_path + ".png"
