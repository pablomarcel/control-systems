
from __future__ import annotations
import subprocess, sys, os, json, pathlib

PKG_DIR = pathlib.Path(__file__).resolve().parents[1]

def test_cli_smoke_no_show(tmp_path):
    cli = PKG_DIR / "cli.py"
    out_json = tmp_path / "tank.json"
    # run for one plant, disable show to be CI-friendly
    cmd = [sys.executable, str(cli), "--plant", "two_tank", "--no-show", "--no-steps", "--no-sigma", "--save-json", str(out_json)]
    res = subprocess.run(cmd, check=True, capture_output=True, text=True)
    # If save-json was given, file should exist (even if also printed to stdout)
    assert out_json.exists()
    data = json.loads(res.stdout)
    assert "summaries" in data
