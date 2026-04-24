from __future__ import annotations
import numpy as np
import control as ct
from pid_controllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner

def test_choose_axes_limits_and_pid_tf():
    cfg = RootLocusConfig(example="ogata_8_1")
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    # prepare a plot target with small a
    L, branches, rays, xlim, ylim = des.prepare_l_and_rays(Gp, a_for_plot=0.5)
    assert branches.ndim == 2
    assert xlim and ylim
    # PID TF
    Gc = des.make_pid_tf(2.0, 1.0, 0.5)
    assert isinstance(Gc, ct.TransferFunction)

def test_analyze_closed_loop():
    cfg = RootLocusConfig(example="ogata_8_1", omega=(0.2, 2.0, 10))
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    perf = des.analyze_closed_loop(Gp, Kp=1.0, Ti=1.0, Td=0.1, settle=0.02)
    # basic keys exist and are floats or None
    for k in ("Mp","Ts","Tr","yss","gm","pm","wg","wp"):
        assert k in perf
