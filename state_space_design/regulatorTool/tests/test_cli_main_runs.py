
from state_space_design.regulatorTool import cli

def test_cli_main_no_plots_capsys():
    argv = [
        "--num","10 20","--den","1 10 24 0",
        "--ts","4.0","--undershoot","0.25,0.35",
        "--plots","none"
    ]
    rc = cli.main(argv)
    assert rc == 0
