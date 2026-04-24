import subprocess, sys, os, json

def test_cli_help_runs():
    cmd = [sys.executable, "-m", "state_space_design.lqrTool.cli", "--help"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0
    assert "LQR" in p.stdout or "usage:" in p.stdout

def test_cli_run_ogata_step(tmp_path):
    # Ogata Example-like
    cmd = [
        sys.executable, "-m", "state_space_design.lqrTool.cli",
        "--A", "0 1 0; 0 0 1; 0 -2 -3",
        "--B", "0; 0; 1",
        "--Q", "diag:100,1,1",
        "--R", "0.01",
        "--C", "1 0 0",
        "--step", "--prefilter", "ogata",
        "--tfinal", "2", "--dt", "0.05",
        "--plots", "none",
        "--export_json", str(tmp_path / "res.json")
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0
    # stdout ends with json
    data = json.loads(p.stdout)
    assert "K" in data and len(data["K"]) > 0
    # file also exists
    assert (tmp_path / "res.json").exists()
