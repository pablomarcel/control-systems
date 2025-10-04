
# tools/diagram.py — optional class diagram generator (requires graphviz)
from __future__ import annotations
def generate_class_diagram(out_path: str = "stateSpaceAnalysis/stateSolnTool/out/stateSolnTool_classes.png"):
    try:
        from graphviz import Digraph
    except Exception:
        print("graphviz not available; skipping diagram.")
        return
    g = Digraph("stateSolnTool", format="png")
    g.attr(rankdir="LR")
    g.node("Realization", "Realization\nA: Matrix\nB: Matrix", shape="record")
    g.node("RealizationFactory", "RealizationFactory", shape="box")
    g.node("StateSolver", "StateSolver\nphi()\nsolve()", shape="box")
    g.node("SolutionVerifier", "SolutionVerifier\nverify()", shape="box")
    g.node("StateSolnEngine", "StateSolnEngine\nrun()", shape="box")
    g.node("StateSolnApp", "StateSolnApp\nrun()", shape="box")
    g.edges([("RealizationFactory","Realization"), ("StateSolnEngine","RealizationFactory"),
             ("StateSolnEngine","StateSolver"), ("StateSolnEngine","SolutionVerifier"),
             ("StateSolnApp","StateSolnEngine")])
    g.render(out_path, cleanup=True)
    print(f"Wrote {out_path}")
