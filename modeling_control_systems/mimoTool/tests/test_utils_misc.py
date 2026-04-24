
from __future__ import annotations
import numpy as np
import control as ct
from modeling_control_systems.mimoTool.utils import get_poles, coerce_outputs_m_by_N

def test_get_poles_from_ss():
    A = np.array([[0.0,1.0],[-2.0,-3.0]]); B = np.eye(2); C = np.eye(2); D = np.zeros((2,2))
    sys = ct.ss(A,B,C,D)
    p = get_poles(sys)
    assert p.shape[0] == 2

def test_coerce_outputs():
    N = 5
    assert coerce_outputs_m_by_N(np.arange(N), N).shape == (1,N)
    assert coerce_outputs_m_by_N(np.arange(N).reshape(N,1), N).shape == (1,N)
    assert coerce_outputs_m_by_N(np.vstack([np.arange(N), np.arange(N)]), N).shape == (2,N)
