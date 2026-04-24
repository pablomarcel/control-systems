
from __future__ import annotations
from control_systems.converterTool.app import ConverterApp
from control_systems.converterTool.apis import ConverterConfig

def test_app_run_ss_only_no_plot():
    app = ConverterApp(level="ERROR")
    cfg = ConverterConfig(
        A="0 1; -2 -3",
        B="1; 0",
        C="1 0",
        D="0",
        no_plot=True
    )
    res = app.run(cfg)
    assert res.mode == "ss"
    assert res.tf is not None

def test_app_run_both_paths_no_plot():
    app = ConverterApp(level="ERROR")
    cfg = ConverterConfig(
        num="1,0", den="1,14,56,160",
        A="0 1 0; 0 0 1; -160 -56 -14",
        B="0;1;-14",
        C="1 0 0",
        D="0",
        no_plot=True
    )
    res = app.run(cfg)
    assert res.mode == "both"
    assert res.tf is not None and res.ss is not None
