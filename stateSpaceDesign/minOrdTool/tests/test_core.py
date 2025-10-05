import numpy as np
from stateSpaceDesign.minOrdTool.core import SystemSpec, MinOrderObserverDesigner, poly_from_roots

def test_basic_design_matches_poles():
    A = np.array([[0,1,0],[0,0,1],[-6,-11,-6]], float)
    C = np.array([[1,0,0]], float)
    sys = SystemSpec(A=A, C=C)
    designer = MinOrderObserverDesigner(sys)
    res = designer.design(poles=np.array([-10,-10], dtype=complex))
    eig = np.linalg.eigvals(res["Ahat"])
    coeff = poly_from_roots(eig)
    desired = poly_from_roots(np.array([-10,-10], dtype=complex))
    assert np.allclose(coeff, desired, rtol=1e-7, atol=1e-8)
