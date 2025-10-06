
import numpy as np, os, pytest
from stateSpaceDesign.observerStatePlotTool.tools.plotting import MplPlotter, PlotlyPlotter

T = np.array([0.0, 0.5, 1.0])
S = [np.array([1.0, 0.5, 0.2]), np.array([0.0, 0.1, 0.2])]
L = ["a","b"]

def test_mpl_plotters(tmp_path):
    mp = MplPlotter(subplots=False, no_show=True)
    out = mp.plot(T, S, L, save_png=str(tmp_path / "a.png"))
    assert os.path.exists(out)
    mp2 = MplPlotter(subplots=True, no_show=True)
    out2 = mp2.plot(T, S, L, save_png=str(tmp_path / "b.png"))
    assert os.path.exists(out2)

def test_plotly_plotters(tmp_path):
    try:
        import plotly  # noqa: F401
    except Exception:
        pytest.skip("Plotly not available")
    pp = PlotlyPlotter(subplots=False)
    out = pp.plot(T, S, L, save_html=str(tmp_path / "a.html"))
    assert os.path.exists(out)
    pp2 = PlotlyPlotter(subplots=True)
    out2 = pp2.plot(T, S, L, save_html=str(tmp_path / "b.html"))
    assert os.path.exists(out2)
