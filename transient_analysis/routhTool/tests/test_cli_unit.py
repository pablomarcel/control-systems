
from __future__ import annotations
import builtins
from transient_analysis.routhTool import cli

def test_cli_direct_call(capsys):
    # Directly invoke the CLI entry function to exercise code paths without spawning a subprocess
    rc = cli.cli([
        "--coeffs", "1, 5, 6, 2",
        "--verify"
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Routh array:" in out
    assert "#RHP roots by Routh" in out
