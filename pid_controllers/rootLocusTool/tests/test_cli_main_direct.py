from __future__ import annotations
from pathlib import Path
from pid_controllers.rootLocusTool import cli

def test_cli_main_no_plot(capsys):
    # Directly call main with argv list to hit parsing & printing paths
    cli.main([
        "--example","ogata_8_1",
        "--zeta_values","0.60","0.70",
        "--omega","0.2","1.0","10",
        "--no_plot",
        "--export_json","pid_controllers/rootLocusTool/out/cli_direct.json"
    ])
    out = capsys.readouterr().out
    assert "Root-Locus (OOP)" in out

def test_cli_main_plotly_save(tmp_path, capsys):
    html_abs = str(tmp_path / "cli_direct_plot.html")
    cli.main([
        "--example","ogata_8_1",
        "--zeta_values","0.60","0.70",
        "--omega","0.2","1.0","10",
        "--backend","plotly",
        "--xlim","-10","2","--ylim","-8","8",
        "--save", html_abs
    ])
    out = capsys.readouterr().out
    assert "Root-Locus (OOP)" in out
