
from __future__ import annotations
from pathlib import Path
from modelingSystems.converterTool import cli

def test_cli_tf_no_plot_sympy_off(tmp_path):
    argv = ["--num","1,0","--den","1,14,56,160","--no-plot"]
    cli.main(argv)

def test_cli_sphinx_skel(tmp_path):
    docs_dir = tmp_path / "docs"
    cli.main(["sphinx-skel", str(docs_dir), "--force"])
    assert (docs_dir / "conf.py").exists()
    assert (docs_dir / "index.rst").exists()
    assert (docs_dir / "api.rst").exists()
    assert (docs_dir / "Makefile").exists()
