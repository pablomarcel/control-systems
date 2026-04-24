import os
import numpy as np
from pathlib import Path

# Ensure repo root on path
here = Path(__file__).resolve()
for p in here.parents:
    if (p / "state_space_design").exists():
        os.environ["PYTHONPATH"] = (str(p) + (":" + os.environ.get("PYTHONPATH","") if os.environ.get("PYTHONPATH") else ""))
        break

from state_space_design.observerGainMatrixTool.core import obsv_matrix, ctrb_matrix, ctrb_dual, phi_of_matrix, is_observable

def test_obsv_ctrb_phi():
    A = np.array([[0,1],[-2,-3]], float)
    B = np.array([[0],[1]], float)
    C = np.array([[1,0]], float)
    Mo = obsv_matrix(A,C)
    Mc = ctrb_matrix(A,B)
    Cd = ctrb_dual(A,C)
    assert Mo.shape == (2,2) and Mc.shape == (2,2) and Cd.shape == (2,2)
    assert bool(is_observable(A,C))
    Mphi = phi_of_matrix(A, np.array([-5,-6], dtype=complex))
    assert Mphi.shape == (2,2)
