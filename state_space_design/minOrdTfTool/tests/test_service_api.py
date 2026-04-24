
import numpy as np
from state_space_design.minOrdTfTool.app import MinOrdTfApp

def test_service_runs_with_explicit_K():
    A = np.array([[0,1],[-2,-3]], float)
    B = np.array([[0],[1]], float)
    C = np.array([[1,0]], float)
    obs_poles = np.array([-5.0], float)
    K = np.array([[6.0, 4.0]], float)

    app = MinOrdTfApp()
    resp = app.run(
        A=A, B=B, C=C,
        obs_poles=obs_poles,
        K=K,
        pretty=False, precision=6, export_json=None
    )
    assert resp.tf_den.size >= 1
