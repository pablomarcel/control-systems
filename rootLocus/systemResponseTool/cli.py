# rootLocus/systemResponseTool/cli.py
from __future__ import annotations
import click
from pathlib import Path

from .apis import RunRequest, SystemResponseService
from .utils import make_logger

@click.group(help="System response tool (step, ramp, impulse, arb, ic1, ic2).")
def cli():
    pass

@cli.command("run", help="Run responses for one or more systems.")
@click.option("--sys", "sys_args", multiple=True, required=True,
              help="System spec string; repeat for multiple. See README or examples.")
@click.option("--responses", required=True,
              help="Comma/space list: step,ramp,impulse,arb,ic1,ic2")
@click.option("--tfinal", type=float, default=5.0, show_default=True)
@click.option("--dt", type=float, default=0.005, show_default=True)
@click.option("--title", type=str, default="")
@click.option("--out-prefix", type=str, default="")
@click.option("--show-input", is_flag=True, help="Overlay input for ramp/arb plots.")
@click.option("--arb-kind", type=click.Choice(["ramp","sine","square","expr","file"]),
              default="ramp", show_default=True)
@click.option("--arb-amp", type=float, default=1.0, show_default=True)
@click.option("--arb-freq", type=float, default=0.5, show_default=True)
@click.option("--arb-duty", type=float, default=0.5, show_default=True)
@click.option("--arb-expr", type=str, default="sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)",
              show_default=True)
@click.option("--arb-file", type=str, default="")
@click.option("--ic-compare/--no-ic-compare", default=True, show_default=True)
@click.option("--log", type=click.Choice(["DEBUG","INFO","WARNING","ERROR"]),
              default="INFO", show_default=True)
def run(sys_args, responses, tfinal, dt, title, out_prefix, show_input,
        arb_kind, arb_amp, arb_freq, arb_duty, arb_expr, arb_file, ic_compare, log):
    logger = make_logger("systemResponseTool")
    logger.setLevel(getattr(__import__("logging").logging, log))
    in_dir = Path(__file__).resolve().parent / "in"
    out_dir = Path(__file__).resolve().parent / "out"

    req = RunRequest(
        sys_args=list(sys_args),
        responses=[r.strip().lower() for r in responses.replace(",", " ").split() if r.strip()],
        tfinal=tfinal, dt=dt, title=title, out_prefix=(out_prefix or None),
        arb_kind=arb_kind, arb_amp=arb_amp, arb_freq=arb_freq, arb_duty=arb_duty,
        arb_expr=arb_expr, arb_file=arb_file, show_input=show_input,
        ic_compare=ic_compare
    )
    svc = SystemResponseService(in_dir, out_dir, show_plots=True)
    svc.run(req)

if __name__ == "__main__":
    cli()
