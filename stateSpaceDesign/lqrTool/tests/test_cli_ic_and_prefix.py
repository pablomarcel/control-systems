import subprocess, sys, os, json, re

def test_cli_initial_only_with_basename_prefix(tmp_path):
    cmd = [
        sys.executable, "-m", "stateSpaceDesign.lqrTool.cli",
        "--A", "0 1; 0 -1",
        "--B", "0; 1",
        "--Q", "eye:2",
        "--R", "1",
        "--x0", "1 0",
        "--tfinal", "0.5",
        "--dt", "0.1",
        "--plots", "none",
        "--save_prefix", "quickrun",
        "--export_json", str(tmp_path / "res.json")
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    # exported file exists
    assert (tmp_path / "res.json").exists()
    # stdout is JSON
    data = json.loads(p.stdout)
    assert "K" in data and "rank_ctrb" in data
