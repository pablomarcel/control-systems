# ---------------------------------
# File: transientAnalysis/icTool/cli.py
# ---------------------------------
from __future__ import annotations
import sys
from pathlib import Path
import click
import numpy as np

from .app import IcToolApp
from .utils import parse_matrix, parse_vector, time_grid


@click.group(help="icTool — response to initial conditions (direct vs step-equivalent)")
def cli():
    pass


@cli.command("compare1", help="Case 1: states — compare direct vs step-equivalent")
@click.option("--A", "A_s", required=True, type=str, help="A matrix e.g. '0 1; -6 -5'")
@click.option("--x0", "x0_s", required=True, type=str, help="Initial state vector e.g. '2; 1'")
@click.option("--tfinal", default=3.0, show_default=True, type=float)
@click.option("--dt", default=0.005, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True, help="Save plot to out/")
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True), help="Base dir for in/out (default: package dir)")
def cmd_compare1(A_s: str, x0_s: str, tfinal: float, dt: float, save: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    A = parse_matrix(A_s); x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    res = app.run_compare1(A, x0, T, save=save)
    click.echo("Compare1 OK — direct and step-equivalent computed.")


@cli.command("compare2", help="Case 2: outputs — compare direct vs step-equivalent")
@click.option("--A", "A_s", required=True, type=str)
@click.option("--C", "C_s", required=True, type=str)
@click.option("--x0", "x0_s", required=True, type=str)
@click.option("--tfinal", default=10.0, show_default=True, type=float)
@click.option("--dt", default=0.01, show_default=True, type=float)
@click.option("--save/--no-save", default=False, show_default=True)
@click.option("--base", default=None, type=click.Path(file_okay=False, dir_okay=True))
def cmd_compare2(A_s: str, C_s: str, x0_s: str, tfinal: float, dt: float, save: bool, base: str | None):
    app = IcToolApp(Path(base) if base else None)
    A = parse_matrix(A_s); C = parse_matrix(C_s); x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    res = app.run_compare2(A, C, x0, T, save=save)
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
    A = parse_matrix(A_s); x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    res = app.run_case1(A, x0, T, save=save)
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
    A = parse_matrix(A_s); C = parse_matrix(C_s); x0 = parse_vector(x0_s)
    T = time_grid(tfinal, dt)
    res = app.run_case2(A, C, x0, T, save=save)
    click.echo("Case2 OK — direct IC outputs computed.")


if __name__ == "__main__":  # pragma: no cover
    cli()