
import sys
from pathlib import Path
import shutil

from control_systems.canonicalTool.cli import main as cli_main

def test_cli_minimal_no_plots_and_docs(tmp_path, capsys, monkeypatch):
    # minimal run
    argv = ["--num","2,3","--den","1,1,10","--no-plots","--no-show"]
    cli_main(argv)
    out = capsys.readouterr().out
    assert "Canonical Conversion Summary" in out

    # sphinx skeleton
    docs_dir = tmp_path / "docs"
    cli_main(["sphinx-skel", str(docs_dir)])
    assert (docs_dir / "conf.py").exists()
    assert (docs_dir / "index.rst").exists()
    assert (docs_dir / "api.rst").exists()
    assert (docs_dir / "Makefile").exists()
