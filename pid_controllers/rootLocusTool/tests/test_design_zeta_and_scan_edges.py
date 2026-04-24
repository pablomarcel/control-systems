from __future__ import annotations
import pytest
import control as ct
from pid_controllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner
import pid_controllers.rootLocusTool.design as dmod

def test_zeta_range_validation_error():
    cfg = RootLocusConfig(example="ogata_8_1", zeta_range=(0.8, 0.2))
    des = RootLocusDesigner(cfg)
    with pytest.raises(ValueError):
        des.zeta_list()

def test_compute_scan_no_a_list(monkeypatch):
    cfg = RootLocusConfig(example="ogata_8_1", zeta_values=[0.6], omega=(0.2, 0.5, 5))
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    # Force internal solver to return empty list
    monkeypatch.setattr(dmod, "_solve_a_on_ray", lambda *a, **k: [])
    rows = des.compute_scan(Gp)
    assert rows == []
