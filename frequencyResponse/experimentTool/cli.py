from __future__ import annotations
import os, sys, json, math
from pathlib import Path
import click
import numpy as np
import control as ct

from .app import ExperimentApp
from .design import ModelSpec, ogata_7_25
from .apis import ExperimentService, fit_simple_from_csv, refine_fit
from .io import read_csv, save_bode_csv, export_summary
from .tools.plot_mpl import plot_bode_mpl
from .tools.plot_plotly import plot_bode_plotly
from .utils import set_verbose, info

PKG_ROOT = Path(__file__).resolve().parent

@click.group(help="Experimental identification via frequency response (Bode + transport lag).")
@click.option("--verbose", is_flag=True, help="Verbose logging.")
@click.option("--delay-method", type=click.Choice(["frd", "pade"]), default="frd")
@click.option("--pade-order", type=int, default=6, show_default=True)
@click.pass_context
def cli(ctx, verbose: bool, delay_method: str, pade_order: int):
    set_verbose(verbose)
    ctx.obj = {"app": ExperimentApp(root=PKG_ROOT, delay_method=delay_method, pade_order=pade_order)}

# Shared options
def model_opts(f):
    f = click.option("--ogata", is_flag=True, help="Use Ogata 7-25 preset.")(f)
    f = click.option("--K", type=float, default=None, help="DC gain K.")(f)
    f = click.option("--type", "lam", type=int, default=None, help="System type λ.")(f)
    f = click.option("--zeros", multiple=True, type=float, help="Zero frequencies ωz.")(f)
    f = click.option("--poles1", multiple=True, type=float, help="First-order pole frequencies ωp.")(f)
    f = click.option("--wns", multiple=True, type=float, help="Natural frequencies ωn for 2nd-order pairs.")(f)
    f = click.option("--zetas", multiple=True, type=float, help="Damping ratios ζ for 2nd-order pairs.")(f)
    f = click.option("--delay", type=float, default=None, help="Transport lag T (s).")(f)
    return f

def grid_opts(f):
    f = click.option("--wmin", type=float, default=0.1)(f)
    f = click.option("--wmax", type=float, default=40.0)(f)
    f = click.option("--npts", type=int, default=1200)(f)
    return f

def plot_opts(f):
    f = click.option("--backend", type=click.Choice(["mpl","plotly","both"]), default="both")(f)
    f = click.option("--save-prefix", default="experimental")(f)
    f = click.option("--no-markers", is_flag=True)(f)
    f = click.option("--nmarkers", type=int, default=40)(f)
    f = click.option("--no-vlines", is_flag=True)(f)
    f = click.option("--export-json", is_flag=True)(f)
    f = click.option("--export-csv", is_flag=True)(f)
    f = click.option("--csv", type=str, default=None, help="Overlay CSV path.")(f)
    return f

@cli.command("run")
@model_opts
@grid_opts
@plot_opts
@click.pass_context
def run_cmd(ctx, **kwargs):
    app: ExperimentApp = ctx.obj["app"]

    # Build ModelSpec (preset or manual with overrides)
    if kwargs["ogata"]:
        spec = ogata_7_25()
    else:
        spec = ModelSpec(
            K=(kwargs["K"] if kwargs["K"] is not None else 1.0),
            lam=(kwargs["lam"] if kwargs["lam"] is not None else 0),
            zeros=list(kwargs["zeros"]) if kwargs["zeros"] else [],
            poles1=list(kwargs["poles1"]) if kwargs["poles1"] else [],
            wns=list(kwargs["wns"]) if kwargs["wns"] else [],
            zetas=list(kwargs["zetas"]) if kwargs["zetas"] else [],
            delay=(kwargs["delay"] if kwargs["delay"] is not None else 0.0),
        )
    spec.clean()

    res = app.run(spec, wmin=kwargs["wmin"], wmax=kwargs["wmax"], npts=kwargs["npts"])
    bode = res["bode"]
    overlay = None
    if kwargs["csv"]:
        D = read_csv(kwargs["csv"])
        overlay = {"w": D["w"], "mag_db": D["mag_db"], "phase_deg": D["phase_deg"], "label":"experimental"}

    prefix = str(app.out_dir / kwargs["save_prefix"])
    outputs = []

    if kwargs["backend"] in ("mpl","both"):
        outputs.append(plot_bode_mpl(bode, spec=spec, title="Bode", path_prefix=f"{prefix}_mpl",
                                     overlay=overlay, markers=(not kwargs["no_markers"]),
                                     nmarkers=kwargs["nmarkers"], vlines=(not kwargs["no_vlines"])))
    if kwargs["backend"] in ("plotly","both"):
        outputs.append(plot_bode_plotly(bode, spec=spec, title="Bode", path_prefix=f"{prefix}_plotly",
                                        overlay=overlay, markers=(not kwargs["no_markers"]),
                                        nmarkers=kwargs["nmarkers"], vlines=(not kwargs["no_vlines"])))

    if kwargs["export_csv"]:
        outputs.append(save_bode_csv(prefix, bode))
    if kwargs["export_json"]:
        sys_for_freq = res["sys"]
        outputs.append(export_summary(prefix, spec, sys_for_freq,
                                      ctx.obj["app"].delay_method,
                                      ctx.obj["app"].pade_order,
                                      diagnostics=None))
    click.echo("Outputs ->")
    for p in outputs:
        click.echo(f" - {p}")

@cli.command("make-csv", help="Generate synthetic CSV from model (use --ogata or flags).")
@model_opts
@grid_opts
@click.option("--csv-out", default=str((PKG_ROOT / "in" / "data.csv").as_posix()))
@click.option("--noise-db", type=float, default=0.0)
@click.option("--noise-deg", type=float, default=0.0)
@click.pass_context
def make_csv_cmd(ctx, **kwargs):
    app: ExperimentApp = ctx.obj["app"]
    spec = ogata_7_25() if kwargs["ogata"] else ModelSpec(
        K=(kwargs["K"] if kwargs["K"] is not None else 1.0),
        lam=(kwargs["lam"] if kwargs["lam"] is not None else 0),
        zeros=list(kwargs["zeros"]) if kwargs["zeros"] else [],
        poles1=list(kwargs["poles1"]) if kwargs["poles1"] else [],
        wns=list(kwargs["wns"]) if kwargs["wns"] else [],
        zetas=list(kwargs["zetas"]) if kwargs["zetas"] else [],
        delay=(kwargs["delay"] if kwargs["delay"] is not None else 0.0),
    )
    spec.clean()
    path = app.synth_csv(spec, wmin=kwargs["wmin"], wmax=kwargs["wmax"], npts=kwargs["npts"],
                         csv_out=kwargs["csv_out"], noise_db=kwargs["noise_db"], noise_deg=kwargs["noise_deg"])
    click.echo(f"Synth CSV written -> {path}")

@cli.command("fit", help="Fit from CSV, optional --refine, then plot/overlay/export.")
@click.option("--csv", type=str, required=True, help="CSV with w, mag_db, phase_deg")
@click.option("--refine", is_flag=True, help="Nonlinear least-squares refinement")
@grid_opts
@plot_opts
@click.pass_context
def fit_cmd(ctx, **kwargs):
    app: ExperimentApp = ctx.obj["app"]
    csv_path = kwargs["csv"]
    svc = ExperimentService(delay_method=app.delay_method, pade_order=app.pade_order)
    spec, diag = svc.fit_from_csv(csv_path, refine=kwargs["refine"])
    res = app.run(spec, wmin=kwargs["wmin"], wmax=kwargs["wmax"], npts=kwargs["npts"])
    bode = res["bode"]
    D = read_csv(csv_path)
    overlay = {"w": D["w"], "mag_db": D["mag_db"], "phase_deg": D["phase_deg"], "label":"experimental"}
    prefix = str(app.out_dir / kwargs["save_prefix"])
    outputs = []
    if kwargs["backend"] in ("mpl","both"):
        outputs.append(plot_bode_mpl(bode, spec=spec, title="Bode", path_prefix=f"{prefix}_mpl",
                                     overlay=overlay, markers=(not kwargs["no_markers"]),
                                     nmarkers=kwargs["nmarkers"], vlines=(not kwargs["no_vlines"])))
    if kwargs["backend"] in ("plotly","both"):
        outputs.append(plot_bode_plotly(bode, spec=spec, title="Bode", path_prefix=f"{prefix}_plotly",
                                        overlay=overlay, markers=(not kwargs["no_markers"]),
                                        nmarkers=kwargs["nmarkers"], vlines=(not kwargs["no_vlines"])))
    if kwargs["export_json"]:
        outputs.append(export_summary(prefix, spec, res["sys"],
                                      app.delay_method, app.pade_order, diagnostics=diag))
    if kwargs["export_csv"]:
        outputs.append(save_bode_csv(prefix, bode))
    click.echo("Outputs ->")
    for p in outputs:
        click.echo(f" - {p}")

if __name__ == "__main__":
    cli()
