
# tools/diagram.py — optional class diagram generator (safe without Graphviz)
from __future__ import annotations

def generate_class_diagram(out_path: str = "stateSpaceAnalysis/stateSolnTool/out/stateSolnTool_classes.png"):
    """
    Generate a simple class diagram if Graphviz *and* its executables are present.
    If anything is missing, return gracefully without raising.
    """
    try:
        from graphviz import Digraph
    except Exception:
        # graphviz python package not installed
        print("graphviz package not available; skipping diagram.")
        return

    try:
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
        # Render may fail if the 'dot' binary is not installed or not on PATH.
        try:
            g.render(out_path, cleanup=True)
            print(f"Wrote {out_path}")
        except Exception as e:
            print(f"Graphviz executable not found or render failed; skipping diagram. Reason: {e}")
            return
    except Exception as e:
        # Catch-all to avoid test failures on older macOS without Graphviz
        print(f"Could not build diagram; skipping. Reason: {e}")
        return
