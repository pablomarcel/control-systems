
from __future__ import annotations
from modeling_control_systems.converterTool.apis import ConverterConfig
from modeling_control_systems.converterTool.app import ConverterApp

def test_cli_like_run_tf_only_no_plot(monkeypatch):
    app = ConverterApp(level="ERROR")
    cfg = ConverterConfig(num="1,0", den="1,14,56,160", no_plot=True, sympy=False)
    res = app.run(cfg)
    assert res.mode == "tf"
    assert res.tf is not None
    assert res.ss is not None
    assert "Transfer function" in (res.pretty_tf or "")
