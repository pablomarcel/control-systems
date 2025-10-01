# rootLocus/systemResponseTool/cli.py
from __future__ import annotations

import os
import sys
import logging as _logging
from pathlib import Path

import click

from .apis import RunRequest, SystemResponseService
from .utils import make_logger


@click.group(help="System response tool (step, ramp, impulse, arb, ic1, ic2).")
def cli():
    """Entry-point for the systemResponseTool CLI."""
    pass


def _strip_conflicting_log_flag(argv: list[str]) -> list[str]:
    """
    Workaround: some global CLI libs (e.g., logistro) claim --log*
    options via argparse and fight Click. We accept a legacy '--log LEVEL'
    pair and rewrite it into '--log-level LEVEL' before Click parses.
    """
    if "--log" in argv:
        try:
            idx = argv.index("--log")
            # If there's a value after it, move it to --log-level
            level = "INFO"
            if idx + 1 < len(argv) and not argv[idx + 1].startswith("-"):
                level = argv[idx + 1]
                # drop both tokens
                new_argv = argv[:idx] + argv[idx + 2 :]
            else:
                new_argv = argv[:idx] + argv[idx + 1 :]
            # insert the safe flag
            new_argv.insert(idx, level)
            new_argv.insert(idx, "--log-level")
            return new_argv
        except Exception:
            # If anything odd happens, just drop the legacy flag
            i = argv.index("--log")
            return argv[:i] + argv[i + 1 :]
    return argv


# Rewrite sys.argv once on import of this module when executed as a module.
if __name__ == "__main__" or (len(sys.argv) > 0 and sys.argv[0].endswith("cli.py")):
    sys.argv = _strip_conflicting_log_flag(sys.argv)


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
@click.option(
    "--log-level", "log_level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO", show_default=True,
    help="Logging verbosity for systemResponseTool."
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
    log_level,
):
    """
    Execute the requested response plots/simulations for the provided system specifications.
    """
    # --- logging level (fixed) ---
    logger = make_logger("systemResponseTool")
    logger.setLevel(getattr(_logging, log_level))

    # Package I/O roots (match exhibit structure)
    pkg_dir = Path(__file__).resolve().parent
    in_dir = pkg_dir / "in"
    out_dir = pkg_dir / "out"

    # Build request DTO (normalize responses list)
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

    # Avoid opening a browser when invoked from pytest subprocess smoke tests
    # (plotly fig.show() can spawn a viewer). Respect normal behavior otherwise.
    show_plots = not bool(os.environ.get("PYTEST_CURRENT_TEST"))

    svc = SystemResponseService(in_dir, out_dir, show_plots=show_plots)
    svc.run(req)


if __name__ == "__main__":
    cli()
