import json
from click.testing import CliRunner
from stateSpaceAnalysis.mimoTool.cli import cli

def test_cli_inproc_help():
    r = CliRunner().invoke(cli, ["--help"])
    assert r.exit_code == 0
    assert "MIMO analysis tool" in r.output

def test_cli_inproc_describe_only():
    # Keep in-process test lightweight due to click I/O edge cases on py3.13.
    r1 = CliRunner().invoke(cli, ["describe", "--plant", "two_tank"])
    assert r1.exit_code == 0
    data = json.loads(r1.output)
    assert "A" in data and "poles" in data
