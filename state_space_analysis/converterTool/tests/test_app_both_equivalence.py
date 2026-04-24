
from __future__ import annotations
from state_space_analysis.converterTool.app import ConverterApp
from state_space_analysis.converterTool.apis import RunRequest

def test_app_both_equivalence_ok(capfd):
    app = ConverterApp()
    req = RunRequest(
        num="1,0", den="1,1,1",
        A="0 1; -1 -1", B="0; 1", C="1 0", D="0",
        no_plot=True
    )
    res = app.run(req)
    assert res.ok
    # capture output to ensure "Equal?" appears (SISO equivalence path)
    out, _ = capfd.readouterr()
    assert "Equal?" in out
