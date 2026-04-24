from __future__ import annotations
import os
import sys
import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """Run a command, capture combined stdout/stderr."""
    env = os.environ.copy()
    # turn on warnings + any optional debug you might add later
    env.setdefault("PYTHONWARNINGS", "default")
    env.setdefault("MC_DEBUG", "1")
    p = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    out = p.communicate()[0]
    return p.returncode, out


def run_cmd(args: list[str]) -> tuple[int, str]:
    # project root is .../modernControl
    repo_root = Path(__file__).resolve().parents[3]
    print("\n===== DEBUG: repo_root =====")
    print(str(repo_root))

    # preflight: where will the CLI import from?
    pre_cmd = [
        sys.executable,
        "-c",
        (
            "import sys,inspect,control; "
            "print('PYVER:', sys.version); "
            "print('control_version:', getattr(control,'__version__','?')); "
            "import pid_controllers.rootLocusTool.cli as m; "
            "print('cli_module_file:', inspect.getfile(m)); "
            "print('sys.path[0]:', sys.path[0])"
        ),
    ]
    print("\n===== DEBUG: preflight import =====")
    pre_rc, pre_out = _run(pre_cmd, repo_root)
    print(pre_out)
    if pre_rc != 0:
        print("Preflight import failed ↑")
        return pre_rc, pre_out

    # actual CLI run
    cmd = [sys.executable, "-m", "pid_controllers.rootLocusTool.cli", *args]
    print("\n===== DEBUG: running CLI =====")
    print("CWD:", str(repo_root))
    print("CMD:", " ".join(cmd))
    rc, out = _run(cmd, repo_root)
    print("\n===== DEBUG: CLI combined stdout/stderr =====")
    print(out)
    print("===== DEBUG: return code:", rc, "=====")
    return rc, out


def test_cli_help_runs():
    code, out = run_cmd(["--help"])
    assert code == 0, f"--help failed (rc={code})\n----- output -----\n{out}\n------------------"
    assert "Root-locus (with ζ-rays)" in out


def test_cli_example_runs_no_plot():
    code, out = run_cmd([
        "--example", "ogata_8_1",
        "--zeta_values", "0.60", "0.65", "0.67", "0.70",
        "--omega", "0.2", "4", "40",
        "--no_plot",
        "--export_json", "pid_controllers/rootLocusTool/out/smoke.json",
    ])
    assert code == 0, f"CLI run failed (rc={code})\n----- output -----\n{out}\n------------------"
    assert "Root-Locus (OOP)" in out
