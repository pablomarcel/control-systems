from __future__ import annotations
from pid_controllers.rootLocusTool.design import RootLocusConfig, RootLocusDesigner

def test_programmatic_scan_summary():
    cfg = RootLocusConfig(example="ogata_8_1", omega=(0.2, 2.0, 20), zeta_values=[0.6, 0.7])
    des = RootLocusDesigner(cfg)
    Gp = des.build_plant()
    pts = des.compute_scan(Gp)
    s = des.summarize_a(pts)
    assert "a_recommended" in s
