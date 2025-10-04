from __future__ import annotations
from pathlib import Path
from pidControllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner
from pidControllers.rootLocusTool.io import plot_plotly

def test_plot_plotly_save_abs(tmp_path):
    cfg = RootLocusConfig(example="ogata_8_1", zeta_values=[0.6], omega=(0.2,1.0,10), xlim=(-10,2), ylim=(-8,8))
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    L, branches, rays, xlim, ylim = des.prepare_l_and_rays(Gp, a_for_plot=0.5)
    html = tmp_path / "plot.html"
    fig = plot_plotly(L, cfg.zeta_values, rays, s_row=None, title="t", xlim=xlim, ylim=ylim, save=str(html))
    assert html.exists()
