from __future__ import annotations
from pathlib import Path

from rootLocus.rootLocusTool.cli import run_cmd as _run_cmd
from rootLocus.rootLocusTool.utils import make_logger

# NOTE:
# _run_cmd is a Click Command object; its underlying function is in .callback

def _tmp_outdir(tmp_path: Path) -> str:
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    return str(out)

def test_cli_runner_tf(tmp_path: Path):
    outdir = _tmp_outdir(tmp_path)
    html = "from_runner_tf.html"

    # Call the Click command's callback directly with kwargs
    _run_cmd.callback(
        poles=None, zeros=None, kgain=1.0,
        num="1,2", den="1,2,3",
        Gnum=None, Gden=None, Hnum=None, Hden=None,
        ssA=None, ssB=None, ssC=None, ssD=None, io=None,
        kpos=None, kneg=None, auto_off=False,
        sgrid=False, zeta="0.7", wn=None,
        no_zeta_labels=False, no_wn_labels=False,
        cg=False, kgains="", cg_absL="", cg_res=181,
        arrows=False, arrow_every=80, arrow_scale=0.04,
        xlim=None, ylim=None,
        klabels="1.34,5.464", title="Root–Locus Tool",
        html=html, png=None, csv=None, outdir=outdir, verbose=False,
    )

    assert (Path(outdir) / html).exists()

def test_cli_runner_series_gh(tmp_path: Path):
    outdir = _tmp_outdir(tmp_path)
    html = "series_gh.html"

    _run_cmd.callback(
        poles=None, zeros=None, kgain=1.0,
        num=None, den=None,
        Gnum="10", Gden="1,1,0", Hnum="1,5", Hden="1,50",
        ssA=None, ssB=None, ssC=None, ssD=None, io=None,
        kpos=None, kneg=None, auto_off=False,
        sgrid=False, zeta="0.6", wn=None,
        no_zeta_labels=False, no_wn_labels=False,
        cg=False, kgains="", cg_absL="", cg_res=181,
        arrows=False, arrow_every=80, arrow_scale=0.04,
        xlim=None, ylim=None,
        klabels="", title="G*H",
        html=html, png=None, csv=None, outdir=outdir, verbose=False,
    )

    assert (Path(outdir) / html).exists()

def test_cli_runner_state_space(tmp_path: Path):
    outdir = _tmp_outdir(tmp_path)
    html = "ss_from_runner.html"

    _run_cmd.callback(
        poles=None, zeros=None, kgain=1.0,
        num=None, den=None,
        Gnum=None, Gden=None, Hnum=None, Hden=None,
        ssA="0,1,0;0,0,1;-160,-56,-14",
        ssB="0;1;-14",
        ssC="1,0,0",
        ssD="0",
        io=None,
        kpos=None, kneg=None, auto_off=False,
        sgrid=True, zeta=None, wn=None,
        no_zeta_labels=False, no_wn_labels=False,
        cg=False, kgains="", cg_absL="", cg_res=181,
        arrows=False, arrow_every=80, arrow_scale=0.04,
        xlim=None, ylim=None,
        klabels="", title="SS",
        html=html, png=None, csv=None, outdir=outdir, verbose=False,
    )

    assert (Path(outdir) / html).exists()

def test_cli_runner_power_switches(tmp_path: Path):
    outdir = _tmp_outdir(tmp_path)
    html = "power_switches.html"

    _run_cmd.callback(
        poles=None, zeros=None, kgain=1.0,
        num="1", den="1,3,2,0",
        Gnum=None, Gden=None, Hnum=None, Hden=None,
        ssA=None, ssB=None, ssC=None, ssD=None, io=None,
        kpos="0,50,50,lin", kneg="0.1,10", auto_off=False,
        sgrid=False, zeta=None, wn=None,
        no_zeta_labels=True, no_wn_labels=True,
        cg=False, kgains="", cg_absL="", cg_res=181,
        arrows=True, arrow_every=40, arrow_scale=0.03,
        xlim=(-3.0, 3.0), ylim=(-3.0, 3.0),
        klabels="", title="Switches",
        html=html, png=None, csv=None, outdir=outdir, verbose=False,
    )

    assert (Path(outdir) / html).exists()
