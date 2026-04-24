"""
CLI entry-point for the MIMO tool.
"""
from __future__ import annotations
import click
import matplotlib
matplotlib.use("Agg")  # headless by default for scripts/tests
from .app import MIMOToolApp

@click.group(help="MIMO analysis tool (state_space_analysis.mimoTool)")
def cli():
    pass

@cli.command("describe")
@click.option("--plant", type=click.Choice(["two_tank","two_zone_thermal"]), required=True)
def cmd_describe(plant):
    app = MIMOToolApp()
    info = app.run_describe(plant)
    import json
    click.echo(json.dumps(info, indent=2, default=str))

@cli.command("steps")
@click.option("--plant", type=click.Choice(["two_tank","two_zone_thermal"]), required=True)
@click.option("--tfinal", type=float, default=100.0, show_default=True)
@click.option("--dt", type=float, default=0.1, show_default=True)
@click.option("--save/--no-save", default=False, show_default=True)
@click.option("--out-prefix", type=str, default=None)
def cmd_steps(plant, tfinal, dt, save, out_prefix):
    app = MIMOToolApp()
    paths = app.run_steps(plant, tfinal=tfinal, dt=dt, save=save, out_prefix=out_prefix)
    if save:
        for p in paths:
            click.echo(p)

@cli.command("sigma")
@click.option("--plant", type=click.Choice(["two_tank","two_zone_thermal"]), required=True)
@click.option("--save/--no-save", default=False, show_default=True)
@click.option("--out-name", type=str, default=None)
def cmd_sigma(plant, save, out_name):
    app = MIMOToolApp()
    path = app.run_sigma(plant, save=save, out_name=out_name)
    if save and path:
        click.echo(path)

if __name__ == "__main__":
    cli()
