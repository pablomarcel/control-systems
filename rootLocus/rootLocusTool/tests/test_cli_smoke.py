from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]  # .../modernControl


def run_cli(args: list[str]) -> tuple[int, str]:
    """Run the CLI and return (returncode, combined stdout+stderr)."""
    cmd = [sys.executable, "-m", "rootLocus.rootLocusTool.cli", *args]
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc.returncode, proc.stdout


def _fail_details(msg: str, code: int, out: str, args: list[str], tmpdir: Path) -> str:
    lines = [
        "=" * 70,
        "CLI smoke test failure",
        f"CWD: {REPO_ROOT}",
        f"ARGS: {' '.join(args)}",
        f"RETURNCODE: {code}",
        f"TEMP DIR: {tmpdir}",
        "-" * 70,
        "STDOUT/STDERR:",
        out,
        "=" * 70,
        msg,
        "=" * 70,
    ]
    return "\n".join(lines)


@pytest.mark.parametrize(
    "args, html_name",
    [
        pytest.param(
            [
                "run",
                "--num", "1,2",
                "--den", "1,2,3",
                "--zeta", "0.7",
                "--klabels", "1.34,5.464",
            ],
            "smoke.html",
            id="tf-run",
        ),
        pytest.param(
            [
                "run",
                "--ssA", "0,1,0;0,0,1;-160,-56,-14",
                "--ssB", "0;1;-14",
                "--ssC", "1,0,0",
                "--ssD", "0",
                "--sgrid",
            ],
            "ss.html",
            id="ss-run",
        ),
    ],
)
def test_cli_smoke(tmp_path: Path, args: list[str], html_name: str):
    # append output params per-case
    full_args = [*args, "--outdir", str(tmp_path), "--html", html_name]
    code, out = run_cli(full_args)

    if code != 0:
        raise AssertionError(_fail_details("CLI returned non-zero exit status.", code, out, full_args, tmp_path))

    # check file creation (full plot or stub)
    html_path = tmp_path / html_name
    if not html_path.exists():
        raise AssertionError(_fail_details(f"Expected HTML not created: {html_path}", code, out, full_args, tmp_path))

    # minimal sanity: should log something recognizable
    if ("Open-loop poles:" not in out) and ("Root–Locus Tool" not in out) and ("[saved] HTML" not in out):
        raise AssertionError(_fail_details("Expected log markers not found in output.", code, out, full_args, tmp_path))
