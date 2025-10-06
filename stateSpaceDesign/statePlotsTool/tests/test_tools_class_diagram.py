
from pathlib import Path
import types
import sys
from stateSpaceDesign.statePlotsTool.tools.class_diagram import generate_class_diagram

class FakeDot:
    def __init__(self, name, format="png"):
        self.format = format
    def node(self, name): pass
    def edge(self, a, b): pass
    def render(self, path, cleanup=True):
        out = str(path) + ".png"
        with open(out, "wb") as f:
            f.write(b"fakepng")
        return out

def test_class_diagram_with_fake_graphviz(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, 'graphviz', types.SimpleNamespace(Digraph=FakeDot))
    out = generate_class_diagram(tmp_path / "uml")
    assert Path(out).suffix == ".png" and Path(out).exists()
