import os
os.environ["MPLBACKEND"] = "Agg"
from click.testing import CliRunner
from pathlib import Path
from transient_analysis.icTool.cli import cli

def test_cli_commands_smoke(tmp_path: Path):
    r = CliRunner().invoke(cli, ["compare1", "--A", "0 1; -6 -5", "--x0", "0.2; 0.1", "--tfinal", "0.1", "--dt", "0.01", "--save", "--base", str(tmp_path)])
    assert r.exit_code == 0

    r = CliRunner().invoke(cli, ["compare2", "--A", "0 1; -6 -5", "--C", "1 0; 0 1", "--x0", "0.2; 0.1", "--tfinal", "0.1", "--dt", "0.01", "--save", "--base", str(tmp_path)])
    assert r.exit_code == 0

    r = CliRunner().invoke(cli, ["case1", "--A", "0 1; -6 -5", "--x0", "0.2; 0.1", "--tfinal", "0.1", "--dt", "0.01", "--save", "--base", str(tmp_path)])
    assert r.exit_code == 0

    r = CliRunner().invoke(cli, ["case2", "--A", "0 1; -6 -5", "--C", "1 0; 0 1", "--x0", "0.2; 0.1", "--tfinal", "0.1", "--dt", "0.01", "--save", "--base", str(tmp_path)])
    assert r.exit_code == 0

    r = CliRunner().invoke(cli, ["tf-step-ogata", "--m", "1", "--b", "3", "--k", "2", "--x0", "0.1", "--v0", "0.05", "--tfinal", "0.1", "--dt", "0.01", "--save", "--json", "--base", str(tmp_path)])
    assert r.exit_code == 0

    r = CliRunner().invoke(cli, ["tf-step", "--num_ic", "0.1 0.05 0", "--den", "1 3 2", "--tfinal", "0.1", "--dt", "0.01", "--save", "--json", "--base", str(tmp_path)])
    assert r.exit_code == 0