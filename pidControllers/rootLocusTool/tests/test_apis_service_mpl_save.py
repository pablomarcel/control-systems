from __future__ import annotations
from pathlib import Path
from pidControllers.rootLocusTool.design import RootLocusConfig
from pidControllers.rootLocusTool.apis import RootLocusService, RootLocusRequest

def test_service_mpl_save(tmp_path):
    cfg = RootLocusConfig(example="ogata_8_1", zeta_values=[0.6], omega=(0.2,1.0,12), xlim=(-10,2), ylim=(-8,8))
    out_png = str(tmp_path / "svc_mpl.png")
    req = RootLocusRequest(cfg=cfg, backend="mpl", save=out_png, analyze=False)
    rep = RootLocusService().run(req)
    # The service shouldn't crash; presence of report fields is enough
    assert "summary" in rep and "a_plot" in rep
