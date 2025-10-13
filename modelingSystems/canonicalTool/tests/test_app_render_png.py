
from pathlib import Path
from modelingSystems.canonicalTool.app import CanonicalApp
from modelingSystems.canonicalTool.apis import RunRequest

def test_app_render_saves_png(tmp_path):
    app = CanonicalApp()
    out_png = tmp_path / "plot.png"
    req = RunRequest(num=[2,3], den=[1,1,10], tfinal=0.5, dt=1e-2, plots=True, no_show=True, save_png=str(out_png))
    res = app.run(req)
    app.render(req, res)
    assert out_png.exists() and out_png.stat().st_size > 0
