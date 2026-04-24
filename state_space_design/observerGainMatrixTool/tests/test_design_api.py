import numpy as np
from state_space_design.observerGainMatrixTool.design import ObserverDesigner
from state_space_design.observerGainMatrixTool.core import obsv_matrix

def test_observer_designer_ack():
    A = np.array([[0,1],[-2,-3]], dtype=float)
    C = np.array([[1,0]], dtype=float)
    poles = np.array([-5,-6], dtype=complex)
    res = ObserverDesigner().compute(A, C, poles, method="ack")
    Ke = res.Ke
    # check stability of A - Ke C
    w = np.linalg.eigvals(A - Ke @ C)
    assert np.all(np.real(w) < -4.99)
