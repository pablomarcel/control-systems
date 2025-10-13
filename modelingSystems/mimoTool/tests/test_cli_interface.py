
from __future__ import annotations
import subprocess, sys, importlib, pathlib

def _cli_file() -> pathlib.Path:
    mod = importlib.import_module("modelingSystems.mimoTool.cli")
    return pathlib.Path(mod.__file__).resolve()

def test_cli_help():
    cli = _cli_file()
    res = subprocess.run([sys.executable, str(cli), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "MIMO examples" in res.stdout

def test_cli_sphinx_skel(tmp_path):
    docs = tmp_path / "docs"
    res = subprocess.run([sys.executable, "-m", "modelingSystems.mimoTool.cli", "sphinx-skel", str(docs)], capture_output=True, text=True, check=True)
    assert (docs / "conf.py").exists()
    assert (docs / "index.rst").exists()
    assert (docs / "api.rst").exists()
