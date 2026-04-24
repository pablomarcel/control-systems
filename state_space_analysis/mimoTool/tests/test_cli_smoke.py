import subprocess, sys, json, os, pathlib

PKG = "state_space_analysis.mimoTool.cli"

def run_cli(args):
    cmd = [sys.executable, "-m", PKG] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=True)

def test_help_runs():
    res = run_cli(["--help"])
    assert "MIMO analysis tool" in res.stdout

def test_describe_json():
    res = run_cli(["describe", "--plant", "two_tank"])
    data = json.loads(res.stdout)
    assert "A" in data and "poles" in data

def test_sigma_saves(tmp_path: pathlib.Path):
    out = tmp_path / "sigma.png"
    res = run_cli(["sigma", "--plant", "two_zone_thermal", "--save", "--out-name", str(out.name)])
    expected = os.path.join("state_space_analysis/mimoTool/out", out.name)
    assert os.path.exists(expected)
