from __future__ import annotations
import numpy as np
import control as ct
from pidControllers.rootLocusTool.core import rlocus_map

class RespA:
    def __init__(self, poles, kvect):
        self.poles = poles
        self.kvect = kvect

class RespB:
    def __init__(self, roots, gains):
        self.roots = roots
        self.gains = gains

def test_rlocus_map_various_shapes(monkeypatch):
    Gp = ct.TransferFunction([1.0],[1.0, 1.0, 0.0])
    n_poles = len(ct.poles(Gp))
    n_g = 5
    # Case A: poles shape (n_g, n_poles) -> must transpose
    arrA = (np.arange(n_g*n_poles).reshape(n_g, n_poles) + 1j*np.zeros((n_g,n_poles)))
    kv = np.linspace(0, 10, n_g)
    monkeypatch.setattr(ct, "root_locus_map", lambda L: RespA(arrA, kv))
    branches, kvect = rlocus_map(Gp)
    assert branches.shape == (n_poles, n_g)
    # Case B: roots shape (n_poles, n_g) -> already oriented
    arrB = (np.arange(n_poles*n_g).reshape(n_poles, n_g) + 1j*np.zeros((n_poles,n_g)))
    monkeypatch.setattr(ct, "root_locus_map", lambda L: RespB(arrB, kv))
    branches2, kvect2 = rlocus_map(Gp)
    assert branches2.shape == (n_poles, n_g)
