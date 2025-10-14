from pathlib import Path
from modelingSystems.systemTool import cli

def test_cli_msd_inprocess_no_save():
    cli.main(["msd-step", "--tfinal", "0.1", "--dt", "0.05", "--no-save"])

def test_cli_tf_from_ss_inprocess():
    cli.main(["tf-from-ss"])

def test_cli_ode_no_deriv_inprocess_no_save():
    cli.main(["ode-no-deriv", "--tfinal", "0.1", "--dt", "0.05", "--no-save"])

def test_cli_ode_with_deriv_inprocess_no_save():
    cli.main(["ode-with-deriv", "--tfinal", "0.1", "--dt", "0.05", "--no-save"])

def test_cli_kv_vs_maxwell_inprocess_no_save():
    cli.main(["kv-vs-maxwell", "--tfinal", "0.1", "--dt", "0.05", "--no-save"])

def test_cli_sphinx_skel(tmp_path):
    d = tmp_path / "docs"
    cli.main(["sphinx-skel", str(d), "--force"])
    assert (d / "conf.py").exists()
