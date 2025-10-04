import subprocess, sys, json, os

PKG = "stateSpaceAnalysis.mimoTool.cli"

def run_cli(args):
    return subprocess.run([sys.executable, "-m", PKG] + args, capture_output=True, text=True, check=True)

def test_cli_steps_save_and_sigma_save():
    # steps save (prints file paths)
    res = run_cli(["steps", "--plant", "two_tank", "--tfinal", "2", "--dt", "0.5", "--save", "--out-prefix", "cli_tt"])
    assert "stateSpaceAnalysis/mimoTool/out" in res.stdout

    # sigma save (prints filepath)
    res2 = run_cli(["sigma", "--plant", "two_zone_thermal", "--save", "--out-name", "cli_sigma.png"])
    out_line = res2.stdout.strip().splitlines()[-1]
    assert out_line.endswith("cli_sigma.png")
    assert os.path.exists(out_line)
