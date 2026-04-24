
from __future__ import annotations
from pathlib import Path
from state_space_analysis.canonicalTool.app import CanonicalToolApp
from state_space_analysis.canonicalTool.design import CompareOptions

def test_plotly_prefers_html_else_png_on_fallback(tmp_path: Path):
    app = CanonicalToolApp()
    save_html = tmp_path / "fallback_{kind}.html"
    opts = CompareOptions(tfinal=0.3, dt=0.01, backend="plotly", show=False, save=str(save_html))
    _ = app.compare(num=[2,3], den=[1,1,10], opts=opts)
    # If Plotly worked, HTML exists; if it failed and we fell back, PNG exists.
    html_path = tmp_path / "fallback_step.html"
    png_path = tmp_path / "fallback_step.png"
    assert html_path.exists() or png_path.exists()
