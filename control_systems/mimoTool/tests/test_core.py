
from __future__ import annotations
import numpy as np
from control_systems.mimoTool.core import MIMOPlantBuilder, MIMOAnalyzer

def test_sigma_shape():
    sys = MIMOPlantBuilder.two_tank()
    w = np.logspace(-2, 2, 50)
    sout = MIMOAnalyzer.sigma_over_frequency(sys, w)
    assert sout.sv.shape == (min(sys.ninputs, sys.noutputs), w.size)

def test_step_dimensions():
    sys = MIMOPlantBuilder.two_zone_thermal()
    outs = MIMOAnalyzer.step_for_each_input(sys, tfinal=1.0, dt=0.1)
    # one StepOut per input
    assert len(outs) == sys.ninputs
    # outputs have shape (m, N)
    for o in outs:
        assert o.Y.shape[0] == sys.noutputs
        assert o.T.ndim == 1
