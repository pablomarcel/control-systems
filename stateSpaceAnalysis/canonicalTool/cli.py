
from __future__ import annotations
import click
from .utils import parse_list
from .design import CompareOptions
from .app import CanonicalToolApp
from .io import default_out_path

@click.group(help="canonicalTool — SISO canonical forms analysis (CCF/OCF/Modal).")
def cli():
    pass

@cli.command("compare", help="Compare CCF/OCF/Modal forms and plot step responses.")
@click.option("--num", type=str, default="2,3", show_default=True, help="numerator coeffs (highest-power-first)")
@click.option("--den", type=str, default="1,1,10", show_default=True, help="denominator coeffs (highest-power-first)")
@click.option("--tfinal", type=float, default=8.0, show_default=True)
@click.option("--dt", type=float, default=1e-3, show_default=True)
@click.option("--symbolic/--no-symbolic", default=False, show_default=True, help="print symbolic G(s) if SymPy available")
@click.option("--backend", type=click.Choice(["mpl", "plotly"], case_sensitive=False), default="mpl", show_default=True)
@click.option("--no_show", is_flag=True, help="disable GUI display")
@click.option("--save", type=str, default=default_out_path("canonical_compare_{kind}.png"), show_default=True,
              help="output path; use {kind} token (e.g., step)")
def compare(num: str, den: str, tfinal: float, dt: float, symbolic: bool, backend: str, no_show: bool, save: str):
    num_v = parse_list(num)
    den_v = parse_list(den)
    app = CanonicalToolApp()
    opts = CompareOptions(tfinal=tfinal, dt=dt, symbolic=symbolic, backend=backend, show=(not no_show), save=save)
    res = app.compare(num=num_v, den=den_v, opts=opts)
    click.echo("TF equality (vs CCF):")
    for k, v in res.tf_equal.items():
        click.echo(f"  {k}: {v}")
    if res.symbolic is not None:
        click.echo("\nSymbolic G(s):")
        click.echo(res.symbolic)

def main():
    cli()

if __name__ == "__main__":
    main()
