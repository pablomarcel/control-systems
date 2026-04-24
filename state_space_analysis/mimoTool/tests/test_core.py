import numpy as np
import matplotlib
matplotlib.use("Agg")
from state_space_analysis.mimoTool.design import PlantFactory
from state_space_analysis.mimoTool.core import MIMOSystem

def test_poles_and_shapes():
    sys = PlantFactory.two_tank()
    p = sys.poles()
    assert p.ndim == 1 and p.size == 2

    T, Y = sys.step_response_per_input(tfinal=1.0, dt=0.5, input_index=0)
    assert Y.shape[0] == sys.noutputs
    assert Y.shape[1] == T.size

def test_sigma_shape():
    sys = PlantFactory.two_zone_thermal()
    w = np.logspace(-2, 1, 20)
    sv = sys.sigma_over_frequency(w)
    assert sv.shape[0] == min(sys.ninputs, sys.noutputs)
    assert sv.shape[1] == w.size
