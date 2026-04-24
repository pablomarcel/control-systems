# root_locus_analysis/compensatorTool/tests/test_cli_parallel.py
from __future__ import annotations

import os
import re
import sys
import subprocess
from textwrap import dedent


PKG_ENTRY = "root_locus_analysis.compensatorTool.cli"


def _env_for_cli() -> dict:
    env = os.environ.copy()
    # Force predictable IO and locale
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "C.UTF-8"
    env["LC_ALL"] = "C.UTF-8"
    # Ensure project root on path (pytest sets rootdir, but be explicit)
    env["PYTHONPATH"] = os.getcwd()
    return env


def _run(argv: list[str]):
    env = _env_for_cli()
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=os.getcwd(),
    )
    out, _ = proc.communicate()
    text = out.decode("utf-8", errors="replace")
    return proc.returncode, text, argv, env


def run_cli(args: list[str]):
    return _run([sys.executable, "-m", PKG_ENTRY] + list(args))


def run_help():
    return run_cli(["parallel", "--help"])


def _click_version() -> str:
    try:
        # run a tiny python snippet in the same venv to fetch click.__version__
        code = "import click, json; print(json.dumps({'click': click.__version__}))"
        rc, out, _, _ = _run([sys.executable, "-c", code])
        if rc == 0 and out.strip():
            return out.strip()
    except Exception:
        pass
    return '{"click":"<unknown>"}'


def _hint_from_trace(text: str) -> str:
    """
    Pulls out common Click errors and emits human-readable hints.
    """
    hints = []

    # Click turns --F-num into 'f_num' kwarg; if function signature uses 'F_num', Click will complain.
    m = re.search(r"got an unexpected keyword argument '([A-Za-z0-9_]+)'.*Did you mean '([A-Za-z0-9_]+)'", text)
    if m:
        bad, sugg = m.group(1), m.group(2)
        hints.append(
            f"[HINT] Click option→kwarg mapping issue: CLI produced '{bad}', "
            f"but the function signature expects '{sugg}'. "
            "Remember: Click lowercases option names to valid identifiers (e.g., '--F-num' → 'f_num')."
        )

    # nargs mismatch / extra argument patterns
    if "requires 2 arguments" in text:
        hints.append(
            "[HINT] The CLI now expects pair-form for '--xlim/--ylim': use '--xlim LO HI' and '--ylim LO HI'."
        )
    elif "Got unexpected extra argument" in text:
        hints.append(
            "[HINT] Looks like an nargs/shape mismatch for an option. "
            "Ensure '--xlim/--ylim' are passed as two separate args: '--xlim -7 1', '--ylim -14 14'."
        )

    if "nargs=-1 is not supported for options" in text:
        hints.append(
            "[HINT] Click does not allow 'nargs=-1' for options; use a fixed arity "
            "(e.g., nargs=2) or parse a single string and split internally."
        )

    return "\n".join(hints) if hints else ""


def _on_fail_dump(name: str, code: int, out: str, argv, env, extra: str = "") -> str:
    help_rc, help_out, help_argv, _ = run_help()
    chunk_help = dedent(
        f"""
        ----- EXTRA: `parallel --help` (rc={help_rc}) ---------------------------
        Command: {' '.join(help_argv)}
        ------------------------------------------------------------------------
        {help_out}
        ------------------------------------------------------------------------
        """
    )
    return dedent(
        f"""
        --- DEBUG ({name}) -----------------------------------------------------
        Return code: {code}
        Command: {' '.join(argv)}
        CWD (intended): {os.getcwd()}
        PYTHONPATH used: {env.get('PYTHONPATH','<none>')}
        PYTHONIOENCODING: {env.get('PYTHONIOENCODING')}
        LANG/LC_ALL: {env.get('LANG')} / {env.get('LC_ALL')}
        CLICK: {_click_version()}
        ------------------------------------------------------------------------
        Captured output (stdout+stderr):
        {out}
        ------------------------------------------------------------------------
        {_hint_from_trace(out)}
        {extra}
        {chunk_help}
        """
    ).strip()


# -----------------------------------------------------------------------------
# Smoke: help
# -----------------------------------------------------------------------------
def test_cli_parallel_help():
    code, out, argv, env = run_cli(["parallel", "--help"])
    if code != 0:
        print(_on_fail_dump("parallel--help", code, out, argv, env))
    assert code == 0
    # Quick sanity that we're reading the right help text
    assert "Parallel compensation via series-equivalent" in out
    assert "--A-num" in out and "--B-num" in out
    assert "--F-num" in out and "--F-den" in out
    assert "--g1-num" in out and "--gcb-den" in out


# -----------------------------------------------------------------------------
# A+K·B split: single design point (zeta+wn)
# -----------------------------------------------------------------------------
def test_cli_parallel_split_single_point():
    # Baseline: pair-form for --xlim and --ylim to match nargs=2
    args = [
        "parallel",
        "--A-num", "1,5,4,20",
        "--B-num", "1,0",
        "--zeta", "0.4",
        "--wn", "3.0",          # concrete wn for a single s*
        "--scale", "20",
        "--legend", "outside",
        "--xlim", "-7", "1",    # pair form
        "--ylim", "-14", "14",  # pair form
    ]
    code, out, argv, env = run_cli(args)

    # If this fails, try a second time also using pair-form, then dump both.
    if code != 0:
        alt_args = [
            "parallel",
            "--A-num", "1,5,4,20",
            "--B-num", "1,0",
            "--zeta", "0.4",
            "--wn", "3.0",
            "--scale", "20",
            "--legend", "outside",
            "--xlim", "-7", "1",
            "--ylim", "-14", "14",
        ]
        alt_code, alt_out, alt_argv, _ = run_cli(alt_args)
        extra = dedent(
            f"""
            ----- ALT ATTEMPT (pair-form x/ylim) (rc={alt_code}) ----------------
            Command: {' '.join(alt_argv)}
            ------------------------------------------------------------------------
            {alt_out}
            ------------------------------------------------------------------------
            """
        )
        print(_on_fail_dump("parallel split single", code, out, argv, env, extra=extra))

    assert code == 0
    assert "== Parallel Compensation via Series-Equivalent ==" in out
    assert "F(s) from A+K·B split" in out
    assert "Series-equivalent loop:" in out
    # Either flavor of the header text is fine depending on implementation
    assert ("Solutions (on ζ-line" in out) or ("Solutions (on ζ-line if applicable)" in out)


# -----------------------------------------------------------------------------
# Direct F(s): single design point via (sreal, wimag)
# -----------------------------------------------------------------------------
def test_cli_parallel_direct_single_point():
    args = [
        "parallel",
        "--F-num", "1,0",
        "--F-den", "1,5,4,20",
        "--sreal", "-1.0490",
        "--wimag", "2.4065",
        "--scale", "20",
    ]
    code, out, argv, env = run_cli(args)

    if code != 0:
        # Try the lower-case spelling in case the CLI only accepted that form.
        alt_args = [
            "parallel",
            "--f-num", "1,0",
            "--f-den", "1,5,4,20",
            "--sreal", "-1.0490",
            "--wimag", "2.4065",
            "--scale", "20",
        ]
        alt_code, alt_out, alt_argv, _ = run_cli(alt_args)
        extra = dedent(
            f"""
            ----- ALT ATTEMPT (lowercase options) (rc={alt_code}) ---------------
            Command: {' '.join(alt_argv)}
            ------------------------------------------------------------------------
            {alt_out}
            ------------------------------------------------------------------------
            """
        )
        print(_on_fail_dump("parallel direct single", code, out, argv, env, extra=extra))

    assert code == 0
    assert "F(s) direct" in out
    assert "Series-equivalent loop:" in out
    assert "k = K/scale" in out


# -----------------------------------------------------------------------------
# Blocks → Gf, then F = Gc_base * Gf: single design point (zeta+wn)
# -----------------------------------------------------------------------------
def test_cli_parallel_blocks_single_point():
    args = [
        "parallel",
        "--g1-num", "20", "--g1-den", "1,5,4",
        "--g2-num", "1",  "--g2-den", "1",
        "--h-num",  "1",  "--h-den",  "1,0",
        "--gcb-num", "1", "--gcb-den", "1,5,4",
        "--zeta", "0.4",
        "--wn", "3.0",
        "--scale", "20",
    ]
    code, out, argv, env = run_cli(args)

    if code != 0:
        # Also try the A+K·B split form that is equivalent numerically; this is
        # just extra noise to help debug in CI without changing assertions.
        alt_args = [
            "parallel",
            "--A-num", "1,5,4,20",
            "--B-num", "1,0",
            "--zeta", "0.4",
            "--wn", "3.0",
            "--scale", "20",
        ]
        alt_code, alt_out, alt_argv, _ = run_cli(alt_args)
        extra = dedent(
            f"""
            ----- ALT ATTEMPT (A+K·B split) (rc={alt_code}) ----------------------
            Command: {' '.join(alt_argv)}
            ------------------------------------------------------------------------
            {alt_out}
            ------------------------------------------------------------------------
            """
        )
        print(_on_fail_dump("parallel blocks single", code, out, argv, env, extra=extra))

    assert code == 0
    assert "F(s) from blocks" in out
    assert "Gf(s) = G2/(1+G1G2H)" in out
    assert "Series-equivalent loop:" in out
