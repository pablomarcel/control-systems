from __future__ import annotations
import types
import control as ct
from pidControllers.rootLocusTool.core import rlocus_map

def test_rlocus_map_fallback(monkeypatch):
    # Build a simple plant
    Gp = ct.TransferFunction([1.0],[1.0,1.0,0.0])
    # Force root_locus_map to raise to hit fallback branch
    monkeypatch.setattr(ct, "root_locus_map", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    branches, kv = rlocus_map(Gp)
    assert branches.shape[0] >= 2
    assert branches.shape[1] >= 2
