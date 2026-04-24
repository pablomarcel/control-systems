import json, os, subprocess, sys, tempfile, pathlib

def test_cli_writes_json(tmp_path):
    cmd = [
        sys.executable, "-m", "state_space_design.minOrdTool.cli",
        "--A", "0 1 0; 0 0 1; -6 -11 -6",
        "--C", "1 0 0",
        "--poles", "-10", "-10",
        "--export-json", str(tmp_path / "out.json"),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert (tmp_path / "out.json").exists()
    data = json.loads((tmp_path / "out.json").read_text())
    assert "Ahat" in data and "Ke" in data
