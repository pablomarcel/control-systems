from __future__ import annotations

# --- import shim so `python cli.py` works with absolute imports ---
import os, sys
if __package__ in (None, ""):
    # When executed as a script, add project root to sys.path
    _pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _pkg_root not in sys.path:
        sys.path.insert(0, _pkg_root)
    # Absolute imports
    from root_locus_analysis.rootLocusTool.apis import RootLocusRequest, RootLocusBatchSpec
    from root_locus_analysis.rootLocusTool.app import RootLocusApp
    from root_locus_analysis.rootLocusTool.io import OutputSpec
    from root_locus_analysis.rootLocusTool.utils import make_logger
else:
    # Normal package execution
    from .apis import RootLocusRequest, RootLocusBatchSpec
    from .app import RootLocusApp
    from .io import OutputSpec
    from .utils import make_logger

import click

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """Root–Locus Tool (object-oriented, testable)"""


@cli.command("run")
# Inputs (TF / ZPK / G*H / state-space)
@click.option("--poles", type=str, default=None)
@click.option("--zeros", type=str, default=None)
@click.option("--kgain", type=float, default=1.0)
@click.option("--num", type=str, default=None)
@click.option("--den", type=str, default=None)
@click.option("--Gnum", type=str, default=None)
@click.option("--Gden", type=str, default=None)
@click.option("--Hnum", type=str, default=None)
@click.option("--Hden", type=str, default=None)
@click.option("--ssA", type=str, default=None)
@click.option("--ssB", type=str, default=None)
@click.option("--ssC", type=str, default=None)
@click.option("--ssD", type=str, default=None)
@click.option("--io", type=int, nargs=2, default=None, metavar="ROW COL")
# K-grid
@click.option("--kpos", type=str, default=None, help='K≥0: "lo,hi,N,lin|log" (omit to auto)')
@click.option("--kneg", type=str, default=None, help='include negative K: "lo,hi"')
@click.option("--auto-off", is_flag=True, help="disable auto K selection")
# s-grid
@click.option("--sgrid", is_flag=True)
@click.option("--zeta", type=str, default=None)
@click.option("--wn", type=str, default=None)
@click.option("--no-zeta-labels", is_flag=True)
@click.option("--no-wn-labels", is_flag=True)
# overlays
@click.option("--cg", is_flag=True)
@click.option("--kgains", type=str, default="")
@click.option("--cg-absL", type=str, default="")
@click.option("--cg-res", type=int, default=181)
# arrows & limits
@click.option("--arrows", is_flag=True)
@click.option("--arrow-every", type=int, default=80)
@click.option("--arrow-scale", type=float, default=0.04)
@click.option("--xlim", type=float, nargs=2, default=None, metavar="XMIN XMAX")
@click.option("--ylim", type=float, nargs=2, default=None, metavar="YMIN YMAX")
# labels & outputs
@click.option("--klabels", type=str, default="")
@click.option("--title", type=str, default="Root–Locus Pro")
@click.option("--html", type=str, default="root_locus.html")
@click.option("--png", type=str, default=None)
@click.option("--csv", type=str, default=None)
@click.option("--outdir", type=str, default="out")
@click.option("--verbose", is_flag=True)
def run_cmd(**kwargs):
    """Run a single root-locus case."""
    # logger first (safe: flag always present due to default)
    verbose = bool(kwargs.pop("verbose"))
    log = make_logger(verbose)

    # helper to read a key with case-insensitive fallback and without KeyError
    def _opt(name):
        return kwargs.get(name) or kwargs.get(name.lower())

    req = RootLocusRequest(
        # Inputs
        poles=_opt("poles"),
        zeros=_opt("zeros"),
        kgain=_opt("kgain"),
        num=_opt("num"),
        den=_opt("den"),
        Gnum=_opt("Gnum"),
        Gden=_opt("Gden"),
        Hnum=_opt("Hnum"),
        Hden=_opt("Hden"),
        ssA=_opt("ssA"),
        ssB=_opt("ssB"),
        ssC=_opt("ssC"),
        ssD=_opt("ssD"),
        io=_opt("io"),
        # K grid
        kpos=_opt("kpos"),
        kneg=_opt("kneg"),
        auto=not bool(kwargs.get("auto_off")),
        # s-grid
        sgrid=bool(kwargs.get("sgrid")),
        zeta=_opt("zeta"),
        wn=_opt("wn"),
        label_zeta=not bool(kwargs.get("no_zeta_labels")),
        label_wn=not bool(kwargs.get("no_wn_labels")),
        # overlays
        cg=bool(kwargs.get("cg")),
        kgains=_opt("kgains"),
        cg_absL=_opt("cg_absL"),
        cg_res=_opt("cg_res"),
        # arrows & limits
        arrows=bool(kwargs.get("arrows")),
        arrow_every=_opt("arrow_every"),
        arrow_scale=_opt("arrow_scale"),
        xlim=_opt("xlim"),
        ylim=_opt("ylim"),
        # labels
        klabels=_opt("klabels"),
        title=_opt("title"),
    )

    outs = OutputSpec(
        out_dir=_opt("outdir"),
        html=_opt("html"),
        png=_opt("png"),
        csv=_opt("csv"),
    )

    RootLocusApp(out_dir=_opt("outdir"), log=log).run(req, outs)


@cli.command("batch")
@click.option("--batch", type=click.Path(exists=True, dir_okay=False), required=True, help="YAML file with a list of cases")
@click.option("--outdir", type=str, default="out")
@click.option("--report", type=str, default="root_locus_report.html")
@click.option("--verbose", is_flag=True)
def batch_cmd(batch, outdir, report, verbose):
    """Run a batch of cases from YAML."""
    # lazy import so PyYAML is not a hard dependency for single-run users/tests
    import yaml
    with open(batch, "r") as f:
        spec = yaml.safe_load(f)
    if not isinstance(spec, list):
        raise click.ClickException("Batch YAML must be a list of case dicts.")
    log = make_logger(verbose)
    app = RootLocusApp(out_dir=outdir, log=log)
    app.run_batch(RootLocusBatchSpec(cases=spec, defaults={}, outdir=outdir, report=report))


if __name__ == "__main__":
    cli()