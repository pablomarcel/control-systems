
from __future__ import annotations
from frequency_response.compensatorTool.app import CompensatorApp

def test_api_ogata_minimal(tmp_path):
    app = CompensatorApp()
    spec = app.spec_ogata_7_28(backend="mpl", plots="bode", save=str(tmp_path / "og728_{kind}.png"), no_show=True)
    result = app.run(spec)
    assert "lag_lead" in result.pack
    assert any(str(p).endswith("_bode.png") for p in result.files)
