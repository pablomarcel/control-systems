import os, numpy as np

os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH","") + (":" if os.environ.get("PYTHONPATH") else "") + "/mnt/data"
from state_space_design.observerGainMatrixTool.design import ObserverDesigner

def test_place_with_jitter_fallback():
    A = np.array([[0,1],[-2,-3]], float)
    C = np.array([[1,0]], float)  # p=1 so multiplicity>1 triggers fallback if requested
    poles = np.array([-5,-5], complex)
    res = ObserverDesigner().compute(A, C, poles, method="place", place_fallback="jitter", jitter_eps=1e-6)
    Ke = res.Ke
    # A - Ke C should be stable near -5
    w = np.linalg.eigvals(A - Ke @ C)
    assert (np.real(w) < -4.9).all()
