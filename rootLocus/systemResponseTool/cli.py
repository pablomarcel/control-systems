# rootLocus/systemResponseTool/cli.py
from __future__ import annotations

# -------------------- sanitize argv ASAP --------------------
import sys as _sys
import os as _os
from pathlib import Path as _Path

def _sanitize_argv_and_capture_legacy_log(argv: list[str]) -> list[str]:
    """
    Accept legacy '--log LEVEL' but *remove* it from argv so argparse-based
    libs never see it. Persist LEVEL in env var SRT_LOG_LEVEL for later.
    """
    # Loud banner (only if user asked for noise)
    if _os.environ.get("SRT_TEST_NOISE"):
        print("[cli] pre-sanitize argv:", argv)

    if "--log" not in argv:
        return argv
    try:
        i = argv.index("--log")
        level = "INFO"
        # if a value is present and not another flag, consume it
        if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
            level = argv[i + 1]
            argv = argv[:i] + argv[i + 2 :]
        else:
            argv = argv[:i] + argv[i + 1 :]
        _os.environ["SRT_LOG_LEVEL"] = level
    except Exception:
        # best-effort drop of the token
        i = argv.index("--log")
        argv = argv[:i] + argv[i + 1 :]

    if _os.environ.get("SRT_TEST_NOISE"):
        print("[cli] post-sanitize argv:", argv)
        print("[cli] SRT_LOG_LEVEL env:", _os.environ.get("SRT_LOG_LEVEL"))

    return argv

_sys.argv = _sanitize_argv_and_capture_legacy_log(list(_sys.argv))

# ------------- import shim for 'python cli.py …' -------------
if __package__ in (None, ""):
    _pkg_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    if _pkg_root not in _sys.path:
        _sys.path.insert(0, _pkg_root)
    # Import via absolute package path
    from rootLocus.systemResponseTool.apis import RunRequest, SystemResponseService
    from rootLocus.systemResponseTool.utils import make_logger
    if _os.environ.get("SRT_TEST_NOISE"):
        print("[cli] import mode: script (__package__ empty). pkg_root=", _pkg_root)
else:
    from .apis import RunRequest, SystemResponseService
    from .utils import make_logger
    if _os.environ.get("SRT_TEST_NOISE"):
        print("[cli] import mode: package (__package__=", __package__, ")")

# Now it's safe to import third-party libs that might look at argv
import logging as _logging
import click


@click.group(help="System response tool (step, ramp, impulse, arb, ic1, ic2).")
def cli():
    """Entry-point for the systemResponseTool CLI."""
    pass


@cli.command("run", help="Run responses for one or more systems.")
@click.option(
    "--sys", "sys_args", multiple=True, required=True,
    help="System spec string; repeat for multiple. See README or examples."
)
@click.option(
    "--responses", required=True,
    help="Comma/space list: step,ramp,impulse,arb,ic1,ic2"
)
@click.option("--tfinal", type=float, default=5.0, show_default=True)
@click.option("--dt", type=float, default=0.005, show_default=True)
@click.option("--title", type=str, default="")
@click.option("--out-prefix", type=str, default="")
@click.option("--show-input", is_flag=True, help="Overlay input for ramp/arb plots.")
@click.option(
    "--arb-kind", type=click.Choice(["ramp", "sine", "square", "expr", "file"]),
    default="ramp", show_default=True
)
@click.option("--arb-amp", type=float, default=1.0, show_default=True)
@click.option("--arb-freq", type=float, default=0.5, show_default=True)
@click.option("--arb-duty", type=float, default=0.5, show_default=True)
@click.option(
    "--arb-expr", type=str,
    default="sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)", show_default=True
)
@click.option("--arb-file", type=str, default="")
@click.option(
    "--ic-compare/--no-ic-compare", default=True, show_default=True,
    help="Overlay step-equivalent curves for IC modes."
)
# Hidden legacy alias to *also* consume '--log LEVEL' if it survived sanitization.
@click.option(
    "--log", "legacy_log_level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default=None, help="(legacy) use --log-level instead.", hidden=True
)
@click.option(
    "--log-level", "log_level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO", show_default=True,
    help="Logging verbosity (legacy '--log LEVEL' also accepted)."
)
def run(
    sys_args,
    responses,
    tfinal,
    dt,
    title,
    out_prefix,
    show_input,
    arb_kind,
    arb_amp,
    arb_freq,
    arb_duty,
    arb_expr,
    arb_file,
    ic_compare,
    legacy_log_level,
    log_level,
):
    """
    Execute the requested response plots/simulations for the provided system specifications.
    """
    # Determine the effective level (env from sanitizer > explicit legacy flag > modern flag)
    effective_level = (
        _os.environ.get("SRT_LOG_LEVEL")
        or legacy_log_level
        or log_level
    )

    if _os.environ.get("SRT_TEST_NOISE"):
        print("[cli.run] legacy_log_level =", legacy_log_level)
        print("[cli.run] log_level        =", log_level)
        print("[cli.run] effective_level  =", effective_level)
        print("[cli.run] CWD              =", _os.getcwd())
        print("[cli.run] in/out dirs will be package local ./in, ./out")

    logger = make_logger("systemResponseTool")
    logger.setLevel(getattr(_logging, str(effective_level), _logging.INFO))

    pkg_dir = _Path(__file__).resolve().parent
    in_dir = pkg_dir / "in"
    out_dir = pkg_dir / "out"

    resp_list = [r.strip().lower() for r in responses.replace(",", " ").split() if r.strip()]
    req = RunRequest(
        sys_args=list(sys_args),
        responses=resp_list,
        tfinal=tfinal,
        dt=dt,
        title=title,
        out_prefix=(out_prefix or None),
        arb_kind=arb_kind,
        arb_amp=arb_amp,
        arb_freq=arb_freq,
        arb_duty=arb_duty,
        arb_expr=arb_expr,
        arb_file=arb_file,
        show_input=show_input,
        ic_compare=ic_compare,
    )

    # Avoid opening a browser during tests
    show_plots = not bool(_os.environ.get("PYTEST_CURRENT_TEST"))

    svc = SystemResponseService(in_dir, out_dir, show_plots=show_plots)
    svc.run(req)


if __name__ == "__main__":
    cli()
