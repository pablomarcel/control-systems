
from __future__ import annotations
from pathlib import Path
from stateSpaceAnalysis.canonicalTool.apis import CanonicalAPI
from stateSpaceAnalysis.canonicalTool.app import CanonicalToolApp
from stateSpaceAnalysis.canonicalTool.design import CompareOptions

def test_api_compare_smoke(tmp_path: Path):
    api = CanonicalAPI()
    res = api.compare(num=[2,3], den=[1,1,10], tfinal=0.5, dt=0.01, symbolic=False, backend="mpl", show=False,
                      save=str(tmp_path / "cmp_{kind}.png"))
    assert "tf_equal" in res and isinstance(res["tf_equal"], dict)

def test_app_compare_saves_file(tmp_path: Path):
    app = CanonicalToolApp()
    save_path = str(tmp_path / "plot_{kind}.png")
    opts = CompareOptions(tfinal=0.5, dt=0.01, backend="mpl", show=False, save=save_path)
    res = app.compare(num=[2,3], den=[1,1,10], opts=opts)
    f = tmp_path / "plot_step.png"
    assert f.exists()
