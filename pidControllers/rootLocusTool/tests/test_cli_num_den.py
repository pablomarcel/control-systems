from __future__ import annotations
from pathlib import Path
from pidControllers.rootLocusTool import cli

def test_cli_main_with_num_den_no_plot(capsys):
    # simple plant: 1 / (s(s+1))
    cli.main([
        "--num", "1",
        "--den", "1 1 0",
        "--zeta_values","0.60","0.70",
        "--omega","0.2","1.0","10",
        "--no_plot",
        "--export_json","pidControllers/rootLocusTool/out/cli_numden.json"
    ])
    out = capsys.readouterr().out
    assert "Root-Locus (OOP)" in out
