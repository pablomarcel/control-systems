# -*- coding: utf-8 -*-
import control as ct
from state_space_design.controllerTool.io import PlotService, PlotConfig

def test_plot_service_noplots_executes():
    ps = PlotService(PlotConfig(plots="none"))
    # Two simple closed-loop TFs
    G1 = ct.tf([1.0],[1.0,1.0])
    G2 = ct.tf([2.0],[1.0,2.0])
    systems = [("A", G1), ("B", G2)]
    # Should run and return without error (no plotting)
    ps.plot_closed_loop_bode_and_step(systems)
