
import numpy as np
import pytest
from stateSpaceDesign.observerStatePlotTool.core import ObserverStateProcessor
from stateSpaceDesign.observerStatePlotTool.utils import parse_time, parse_vec_real

def test_simulate_if_missing_with_scipy():
    try:
        import scipy  # noqa: F401
    except Exception:
        pytest.skip("SciPy not available")
    proc = ObserverStateProcessor()
    # Build a simple stable A_aug (2n x 2n with n=2)
    A_aug = np.diag([-1.0, -2.0, -1.0, -2.0])
    payload = {
        "A_augmented": A_aug.tolist(),
        "C": [[1.0, 0.0]],
        "K": [0.5, 0.2],
    }
    T = parse_time("0:0.1:0.3")
    x0 = parse_vec_real("1 0", 2)
    e0 = parse_vec_real("0 0", 2, default_first_one=False)
    bundle = proc.simulate_if_missing(payload, T, x0, e0)
    assert bundle.X.shape == (2, len(T))
    assert bundle.E.shape == (2, len(T))
    assert bundle.u.shape[0] == len(T)
    # y could be vector (p,N) or flat if p=1; just ensure shapes are compatible
    if getattr(bundle.y, "ndim", 1) == 1:
        assert bundle.y.shape[0] == len(T)
    else:
        assert bundle.y.shape[1] == len(T)
