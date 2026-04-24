import numpy as np
from control_systems.systemTool.core import build_mass_spring_damper, companion_state_space, build_ss_with_deriv

def test_msd_shapes():
    sys = build_mass_spring_damper(1.0, 1.0, 10.0)
    assert sys.A.shape == (2,2)
    assert sys.B.shape == (2,1)
    assert sys.C.shape == (1,2)
    assert sys.D.shape == (1,1)

def test_companion_simple():
    A,B,C,D = companion_state_space([1.0, 10.0], 1.0)
    assert A.shape == (2,2) and B.shape == (2,1)
    assert C[0,0] == 1.0 and D[0,0] == 0.0

def test_with_deriv_beta():
    a=[1.0,10.0]; b=[0.5,1.0,0.0]
    A,B,C,D,beta = build_ss_with_deriv(a,b)
    assert len(beta)==3
    assert D.shape==(1,1)
