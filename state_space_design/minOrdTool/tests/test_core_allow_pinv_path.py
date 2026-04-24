
import numpy as np
from state_space_design.minOrdTool.core import SystemSpec, MinOrderObserverDesigner

def test_allow_pinv_allows_singular_S():
    A = np.zeros((2,2), float)
    C = np.array([[1,0]], float)  # p=1
    sys = SystemSpec(A=A, C=C, B=None)
    desg = MinOrderObserverDesigner(sys)
    res = desg.design(poles=np.array([-1.0]), allow_pinv=True)
    assert res["Ke"].shape == (1,1)
    assert res["Ahat"].shape == (1,1)
