
from pathlib import Path
import numpy as np
from stateSpaceDesign.statePlotsTool.design import CSVExporter, PlotBackend
from stateSpaceDesign.statePlotsTool.core import SimICResult, SimStepResult

def test_csv_exporters(tmp_path):
    t = np.linspace(0,0.5,6)
    X = np.vstack([t, t**2])
    ic_res = SimICResult(t=t, X=X, labels=["x1","x2"])
    step_res = SimStepResult(t=t, series=[t, t**2], labels=["y1","x1"], kind="both")
    c = CSVExporter()
    ic_csv = c.save_ic(ic_res, filename="ic.csv", out_dir=tmp_path)
    st_csv = c.save_step(step_res, filename="st.csv", out_dir=tmp_path)
    assert Path(ic_csv).exists() and Path(st_csv).exists()

def test_plot_backends_mpl_and_plotly(tmp_path):
    t = np.linspace(0,0.5,6)
    series = [t, t**2]
    labels = ["a","b"]
    p = PlotBackend(subplots=True)
    png = p.mpl(t, series, labels, "T", "Y", filename_png="plot.png", out_dir=tmp_path)
    assert Path(png).exists()
    try:
        html = p.plotly(t, series, labels, "T", "Y", filename_html="plot.html", out_dir=tmp_path)
        assert Path(html).exists()
    except RuntimeError:
        pass
