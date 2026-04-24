from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")  # headless
from pid_controllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner
from pid_controllers.rootLocusTool.io import plot_mpl

def test_io_mpl_save(tmp_path):
    cfg = RootLocusConfig(example="ogata_8_1", omega=(0.2, 1.0, 12), zeta_values=[0.6])
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    L, branches, rays, xlim, ylim = des.prepare_l_and_rays(Gp, a_for_plot=0.5)
    out_png = tmp_path / "out.png"
    # save relative to CWD via ensure_out_path logic; here we pass absolute to be safe
    fig, ax = plot_mpl(L, cfg.zeta_values or [], rays, s_star=None, title="t", xlim=xlim, ylim=ylim, save=str(out_png))
    assert os.path.exists(out_png)
