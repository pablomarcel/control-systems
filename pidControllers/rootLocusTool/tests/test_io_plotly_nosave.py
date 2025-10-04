from __future__ import annotations
import control as ct
from pidControllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner
from pidControllers.rootLocusTool.io import plot_plotly

def test_plot_plotly_nosave():
    cfg = RootLocusConfig(example="ogata_8_1", zeta_values=[0.6], omega=(0.2,1.0,10))
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    L, branches, rays, xlim, ylim = des.prepare_l_and_rays(Gp, a_for_plot=0.5)
    # minimal s_row dict
    s_row = dict(zeta=0.6, omega=0.8, a=0.5, K=1.0, Kp=0.6, Ti=2.0, Td=0.5, sigma=-0.3, jw=0.8)
    fig = plot_plotly(L, cfg.zeta_values, rays, s_row=s_row, title="t", xlim=xlim, ylim=ylim, save=None)
    assert fig is not None
