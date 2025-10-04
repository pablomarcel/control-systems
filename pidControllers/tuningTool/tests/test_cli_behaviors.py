
from __future__ import annotations
import sys, subprocess, os, json
from pathlib import Path

def _write_rules(path: Path):
    path.write_text(json.dumps({
        "methods": {
            "ZN_step": {
                "name": "First",
                "inputs": ["L","T"],
                "controllers": {
                    "PID": { "formula": { "Kp":"1.2*T/L","Ti":"2*L","Td":"0.5*L" } }
                }
            }
        }
    }, indent=2), encoding="utf-8")

def _repo_root(start: Path) -> Path:
    p = start.resolve()
    while True:
        if (p / "pidControllers").is_dir():
            return p
        if p.parent == p:
            raise RuntimeError("Repo root not found")
        p = p.parent

def test_cli_lists_and_errors(tmp_path: Path):
    json_path = tmp_path / "rules.json"
    _write_rules(json_path)
    REPO_ROOT = _repo_root(Path(__file__))
    env = dict(os.environ); env["PYTHONPATH"] = str(REPO_ROOT)

    # list methods
    p1 = subprocess.run([sys.executable, "-m", "pidControllers.tuningTool.cli", "--file", str(json_path), "--list", "methods"],
                        cwd=REPO_ROOT, capture_output=True, text=True, env=env)
    assert p1.returncode == 0 and "ZN_step" in p1.stdout

    # missing required inputs
    p2 = subprocess.run([sys.executable, "-m", "pidControllers.tuningTool.cli", "--file", str(json_path),
                         "--method","ZN_step","--controller","PID"],
                        cwd=REPO_ROOT, capture_output=True, text=True, env=env)
    assert p2.returncode != 0
    assert "requires inputs" in p2.stdout or "requires inputs" in p2.stderr

def test_cli_export_json_csv(tmp_path: Path):
    json_path = tmp_path / "rules.json"
    _write_rules(json_path)
    REPO_ROOT = _repo_root(Path(__file__))
    env = dict(os.environ); env["PYTHONPATH"] = str(REPO_ROOT)

    # export files
    p = subprocess.run([sys.executable, "-m", "pidControllers.tuningTool.cli", "--file", str(json_path),
                        "--method","ZN_step","--controller","PID","--L","0.8","--T","3.0",
                        "--export-json","res.json","--export-csv","res.csv"],
                        cwd=REPO_ROOT, capture_output=True, text=True, env=env)
    assert p.returncode == 0
    # ensure CLI reported saved files (paths are printed by the CLI)
    assert "Saved JSON" in p.stdout
    assert "Saved CSV" in p.stdout
