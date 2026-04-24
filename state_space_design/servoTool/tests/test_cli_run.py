import json, sys, pathlib, subprocess, os

def _write_json(tmp_path, content, name):
    p = tmp_path / name
    p.write_text(json.dumps(content), encoding="utf-8")
    return str(p)

def test_cli_run_k_mode(tmp_path):
    ctrl = {
        "mode": "K",
        "A": [[0,1],[0,-2]],
        "B": [[0],[1]],
        "K": [2,3],
        "state_names": ["x1","x2"],
        "output_names": ["y1"]
    }
    data = _write_json(tmp_path, ctrl, "K_controller.json")

    cmd = [sys.executable, "-m", "state_space_design.servoTool.cli",
           "--data", data, "--C", "1 0",
           "--export_json", "cli_k_io.json",
           "--save_csv", "cli_k_step.csv",
           "--backend", "none",
           "--t", "0:0.1:1"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "ServoTool results" in proc.stdout
    assert "k_r:" in proc.stdout

def test_cli_run_ki_mode(tmp_path):
    ctrl = {
        "mode": "KI",
        "A": [[0,1],[0,-2]],
        "B": [[0],[1]],
        "C": [[1,0]],
        "K": [2,3],
        "kI": 4.0,
        "state_names": ["x1","x2"],
        "output_names": ["y1"]
    }
    data = _write_json(tmp_path, ctrl, "KI_controller.json")

    cmd = [sys.executable, "-m", "state_space_design.servoTool.cli",
           "--data", data,
           "--export_json", "cli_ki_io.json",
           "--save_csv", "cli_ki_step.csv",
           "--backend", "none",
           "--t", "0:0.1:1"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "kI:" in proc.stdout
