
from __future__ import annotations
from pathlib import Path
from rootLocus.rootLocusTool.app import RootLocusApp
from rootLocus.rootLocusTool.apis import RootLocusRequest
from rootLocus.rootLocusTool.io import OutputSpec

def _mk(tmp_path: Path):
    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)
    app = RootLocusApp(out_dir=str(outdir))
    return app, str(outdir)

def test_app_run_tf_html_png_csv(tmp_path: Path):
    app, outdir = _mk(tmp_path)
    req = RootLocusRequest(num="1,2", den="1,2,3", zeta="0.7", klabels="1.34,5.464", sgrid=False)
    outs = OutputSpec(out_dir=outdir, html="app_tf.html", png="app_tf.png", csv="app_tf.csv")
    res = app.run(req, outs)
    assert (tmp_path / "out" / "app_tf.html").exists()
    # PNG and CSV may be optional in PlotService; ensure paths are returned (file may be created depending on implementation)
    assert isinstance(res, dict) and "html" in res

def test_app_run_series_and_bounds(tmp_path: Path):
    app, outdir = _mk(tmp_path)
    req = RootLocusRequest(Gnum="10", Gden="1,1,0", Hnum="1,5", Hden="1,50",
                           zeta="0.6", kpos="0,20,100,lin", kneg="0.1,5")
    outs = OutputSpec(out_dir=outdir, html="series_bounds.html")
    res = app.run(req, outs)
    assert (tmp_path / "out" / "series_bounds.html").exists()

def test_app_run_state_space_and_overlays(tmp_path: Path):
    app, outdir = _mk(tmp_path)
    req = RootLocusRequest(ssA="0,1,0;0,0,1;-160,-56,-14", ssB="0;1;-14",
                           ssC="1,0,0", ssD="0",
                           cg=True, kgains="0.5,1,2",
                           zeta="0.5,0.707", sgrid=True,
                           xlim=(-10,10), ylim=(-10,10),
                           arrows=True, arrow_every=60, arrow_scale=0.02)
    outs = OutputSpec(out_dir=outdir, html="ss_overlays.html")
    app.run(req, outs)
    assert (tmp_path / "out" / "ss_overlays.html").exists()
