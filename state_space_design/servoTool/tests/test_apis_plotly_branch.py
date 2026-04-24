import sys, types, json
from state_space_design.servoTool.apis import run, RunRequest

class _FakeGO(types.SimpleNamespace):
    class Figure:
        def __init__(self): pass
        def add_trace(self, *a, **k): pass
        def update_layout(self, **k): pass
        def to_html(self, **k): return "<html></html>"
    class Scatter:
        def __init__(self, *a, **k): pass

def test_apis_plotly_with_fake_module(tmp_path, monkeypatch):
    fake_pkg = types.ModuleType("plotly")
    graph_objects_mod = types.ModuleType("plotly.graph_objects")
    graph_objects_mod.Figure = _FakeGO.Figure
    graph_objects_mod.Scatter = _FakeGO.Scatter
    sys.modules["plotly"] = fake_pkg
    sys.modules["plotly.graph_objects"] = graph_objects_mod

    ctrl = {
        "mode": "KI",
        "A": [[0,1],[0,-2]],
        "B": [[0],[1]],
        "C": [[1,0]],
        "K": [2,3],
        "kI": 1.0
    }
    p = tmp_path / "ctrl.json"
    p.write_text(json.dumps(ctrl), encoding="utf-8")

    req = RunRequest(
        data_path=str(p),
        r=1.0,
        export_json="apis_ki_io.json",
        t="0:0.1:1",
        backend="plotly",
        no_show=True,
    )
    resp = run(req)
    assert resp.plot_html_path is not None
    assert resp.plot_html_path.endswith("servo_plot.html")
