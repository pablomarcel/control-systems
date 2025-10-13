
from __future__ import annotations
"""
Quick-and-dirty class diagram using graphviz.

Usage:
    python -m modelingSystems.mimoTool.tools.tool_class_diagram --out out/mimoTool_classes
"""
import argparse, os
from graphviz import Digraph

CLASSES = [
    ("MIMOPlantBuilder", []),
    ("MIMOAnalyzer", []),
    ("MIMOPlotter", []),
    ("RunConfig", []),
    ("RunResult", ["PlantSummary"]),
    ("PlantSummary", []),
    ("MIMOApp", ["RunConfig","RunResult","MIMOPlantBuilder","MIMOAnalyzer","MIMOPlotter"]),
]

def build(out: str):
    dot = Digraph("mimoTool", format="png")
    dot.attr(rankdir="LR", fontsize="12")
    for cls, deps in CLASSES:
        dot.node(cls, shape="record", label=f"{cls}")
        for d in deps:
            dot.edge(cls, d, arrowhead="vee")
    base, ext = os.path.splitext(out)
    dot.render(base, cleanup=True)
    return base + ".png"

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/mimoTool_class_diagram")
    ns = ap.parse_args(argv)
    os.makedirs(os.path.dirname(ns.out) or ".", exist_ok=True)
    out = build(ns.out)
    print(out)

if __name__ == "__main__":
    main()
