from __future__ import annotations
from pathlib import Path
import importlib.util
import numpy as np

from frequency_response.experimentTool.design import ogata_7_25
from frequency_response.experimentTool.core import build_rational_tf, bode_arrays
from frequency_response.experimentTool.tools.plot_mpl import plot_bode_mpl

def test_plot_mpl_outputs_png(repo_root: Path):
    spec = ogata_7_25()
    G = build_rational_tf(spec)
    w = np.logspace(-1, 2, 64)
    bode = bode_arrays(G, w, spec.delay, delay_method="frd")
    prefix = repo_root / "frequency_response" / "experimentTool" / "out" / "plot_unit"
    png = plot_bode_mpl(bode, spec=spec, title="Bode", path_prefix=str(prefix), overlay=None, markers=False, vlines=False)
    assert Path(png).exists()

def test_plot_plotly_html_if_available(repo_root: Path):
    # Skip if plotly is not installed
    if importlib.util.find_spec("plotly") is None:
        return
    from frequency_response.experimentTool.tools.plot_plotly import plot_bode_plotly
    spec = ogata_7_25()
    G = build_rational_tf(spec)
    w = np.logspace(-1, 2, 32)
    bode = bode_arrays(G, w, spec.delay, delay_method="frd")
    prefix = repo_root / "frequency_response" / "experimentTool" / "out" / "plotly_unit"
    html = plot_bode_plotly(bode, spec=spec, title="Bode", path_prefix=str(prefix), overlay=None, markers=False, vlines=False)
    assert Path(html).exists()
