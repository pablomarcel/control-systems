
from __future__ import annotations
import numpy as np
import control as ct
from frequency_response.compensatorTool import io as IO

def test_export_csvs_and_write_json(tmp_path):
    G = ct.tf([1.0], [1.0, 1.0])
    w = np.logspace(-2, 2, 16)
    out = IO.export_csvs(str(tmp_path/"b"), G, G, w)
    assert all(p.exists() for p in [tmp_path/"b_bode.csv", tmp_path/"b_nichols.csv"])
    p = IO.write_json(str(tmp_path/"x.json"), {"a":1,"b":[1,2]})
    assert (tmp_path/"x.json").exists()

def test_render_plots_mpl(tmp_path, monkeypatch):
    # Avoid popping GUI windows
    monkeypatch.setenv("MPLBACKEND","Agg")
    import matplotlib
    matplotlib.use("Agg")
    G = ct.tf([1.0], [1.0, 1.0])
    w = np.logspace(-2,2,32)
    files = IO.render_plots(
        backend="mpl",
        wants=["bode","nyquist","nichols","step","ramp"],
        G1=G, G_ol_c=G, w=w,
        ogata_axes=True, nichols_templates=True,
        nichols_Mdb=[-12,0,6], nichols_Ndeg=[-60,-120],
        nyquist_M=[1.2], nyquist_marks=[0.2,1.0],
        save_tmpl=str(tmp_path/"out_{kind}.png"),
        save_img_tmpl=None,
        no_show=True,
        show_unstable=True,
    )
    assert any("bode" in f for f in files)
    assert any("nyquist" in f for f in files)
    assert any("nichols" in f for f in files)
    assert any("step" in f for f in files)
    assert any("ramp" in f for f in files)

def test_render_plots_plotly_html(tmp_path):
    G = ct.tf([1.0], [1.0, 1.0])
    w = np.logspace(-2,2,32)
    files = IO.render_plots(
        backend="plotly",
        wants=["bode","nyquist","nichols"],
        G1=G, G_ol_c=G, w=w,
        ogata_axes=False, nichols_templates=False,
        nichols_Mdb=None, nichols_Ndeg=None,
        nyquist_M=[1.2], nyquist_marks=[0.2,1.0],
        save_tmpl=str(tmp_path/"out_{kind}.html"),
        save_img_tmpl=None,
        no_show=True,
        show_unstable=False,
    )
    assert all(f.endswith(".html") for f in files)
