# ---------------------------------
# File: transientAnalysis/icTool/cli.py
# ---------------------------------
from __future__ import annotations

from pathlib import Path
import click

from .app import IcToolApp
from .utils import parse_matrix, parse_vector, time_grid, parse_poly


@click.group(help="icTool — response to initial conditions (direct vs step-equivalent)")
def cli():
    """Top-level CLI group for icTool."""
    pass


# =========================
# State-space oriented cmds
# =========================

@cli.command("compare1", help="Case 1: states — compare direct vs step-equivalent")
@click.option("--A", "A_s", required=True, type=str, help="A matrix e.g. '0 1; -6 -5'")
@click.option("--x0", "x0_s", required=True, type=str, help="Initial state vector e.g. '2; 1'")
@click.option("--tfinal", default=3.0, show_default=True, type=float)
@click.option("--dt", default=0.005, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True, help="Save plot to out/")
@click.option(
    "--base",
    default=None,
    type=click.Path(file_okay=False, dir_okay=True),
    help="Base dir for in/out (default: package dir)",
)
def cmd_compare1(A_s: str, x0_s: str, tfinal: float, dt: float, save: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    A = parse_matrix(A_s)
    x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    _ = app.run_compare1(A, x0, T, save=save)
    click.echo("Compare1 OK — direct and step-equivalent computed.")


@cli.command("compare2", help="Case 2: outputs — compare direct vs step-equivalent")
@click.option("--A", "A_s", required=True, type=str, help="A matrix e.g. '0 1 0; 0 0 1; -10 -17 -8'")
@click.option("--C", "C_s", required=True, type=str, help="C matrix e.g. '1 0 0'")
@click.option("--x0", "x0_s", required=True, type=str, help="Initial state vector e.g. '2; 1; 0.5'")
@click.option("--tfinal", default=10.0, show_default=True, type=float)
@click.option("--dt", default=0.01, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True)
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True))
def cmd_compare2(A_s: str, C_s: str, x0_s: str, tfinal: float, dt: float, save: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    A = parse_matrix(A_s)
    C = parse_matrix(C_s)
    x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    _ = app.run_compare2(A, C, x0, T, save=save)
    click.echo("Compare2 OK — direct and step-equivalent computed.")


@cli.command("case1", help="Case 1: states — direct only")
@click.option("--A", "A_s", required=True, type=str)
@click.option("--x0", "x0_s", required=True, type=str)
@click.option("--tfinal", default=3.0, show_default=True, type=float)
@click.option("--dt", default=0.005, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True)
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True))
def cmd_case1(A_s: str, x0_s: str, tfinal: float, dt: float, save: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    A = parse_matrix(A_s)
    x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    _ = app.run_case1(A, x0, T, save=save)
    click.echo("Case1 OK — direct IC states computed.")


@cli.command("case2", help="Case 2: outputs — direct only")
@click.option("--A", "A_s", required=True, type=str)
@click.option("--C", "C_s", required=True, type=str)
@click.option("--x0", "x0_s", required=True, type=str)
@click.option("--tfinal", default=3.0, show_default=True, type=float)
@click.option("--dt", default=0.005, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True)
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True))
def cmd_case2(A_s: str, C_s: str, x0_s: str, tfinal: float, dt: float, save: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    A = parse_matrix(A_s)
    C = parse_matrix(C_s)
    x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    _ = app.run_case2(A, C, x0, T, save=save)
    click.echo("Case2 OK — direct IC outputs computed.")


# =========================
# Transfer-function cmds
# =========================

@cli.command(
    "tf-step-ogata",
    help="TF step-equivalent output via Ogata Ex. 5-8 parameters (m,b,k,x0,v0)",
)
@click.option("--m", type=float, required=True, help="Mass m")
@click.option("--b", type=float, required=True, help="Damping b")
@click.option("--k", type=float, required=True, help="Stiffness k")
@click.option("--x0", type=float, required=True, help="Initial displacement x(0)")
@click.option("--v0", type=float, required=True, help="Initial velocity ẋ(0)")
@click.option("--tfinal", default=5.0, show_default=True, type=float)
@click.option("--dt", default=0.01, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True, help="Save plot to out/")
@click.option("--json/--no-json", "save_json", default=False, show_default=True, help="Save series to JSON in out/")
@click.option("--analytic/--no-analytic", default=False, show_default=True, help="Overlay analytic solution when available")
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True), help="Base dir for in/out (default: package dir)")
def cmd_tf_step_ogata(
    m: float, b: float, k: float, x0: float, v0: float, tfinal: float, dt: float,
    save: bool, save_json: bool, analytic: bool, base: str | None
):
    app = IcToolApp(Path(base) if base else None)
    T = time_grid(tfinal, dt)
    app.run_tf_step_ogata(m, b, k, x0, v0, T, save=save, save_json=save_json, overlay_analytic=analytic)
    click.echo("TF step (Ogata) OK — computed and handled outputs.")


@cli.command(
    "tf-step",
    help="TF step-equivalent output from explicit numerator/denominator for G_ic(s)",
)
@click.option("--num_ic", type=str, required=True, help="Numerator coeffs for G_ic(s), e.g. '1 0.5 0'")
@click.option("--den", type=str, required=True, help="Denominator coeffs, e.g. '1 3 2'")
@click.option("--tfinal", default=5.0, show_default=True, type=float)
@click.option("--dt", default=0.01, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True, help="Save plot to out/")
@click.option("--json/--no-json", "save_json", default=False, show_default=True, help="Save series to JSON in out/")
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True), help="Base dir for in/out (default: package dir)")
def cmd_tf_step(num_ic: str, den: str, tfinal: float, dt: float, save: bool, save_json: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    T = time_grid(tfinal, dt)
    ni = parse_poly(num_ic)
    dd = parse_poly(den)
    app.run_tf_step_generic(ni, dd, T, save=save, save_json=save_json)
    click.echo("TF step (generic) OK — computed and handled outputs.")


if __name__ == "__main__":  # pragma: no cover
    cli()
