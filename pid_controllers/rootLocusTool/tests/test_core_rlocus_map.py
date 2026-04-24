from __future__ import annotations
import numpy as np
import control as ct
from pid_controllers.rootLocusTool.core import rlocus_map

def test_rlocus_map_shape():
    # L = K * 1/(s(s+1))
    Gp = ct.TransferFunction([1.0],[1.0,1.0,0.0])
    branches, kv = rlocus_map(Gp)
    assert branches.ndim == 2
    # branches: (n_branches, n_gains)
    assert branches.shape[0] >= 2
    assert branches.shape[1] >= 2
    assert isinstance(kv, np.ndarray)
