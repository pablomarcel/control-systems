
from __future__ import annotations
import pathlib, importlib
from typing import Iterable

cli = importlib.import_module("transient_analysis.responseTool.cli")

PKG_OUT = pathlib.Path("transient_analysis/responseTool/out")  # fallback

def _pick(path1: pathlib.Path, name: str) -> pathlib.Path | None:
    p1 = path1 / "out" / name
    if p1.exists():
        return p1
    p2 = PKG_OUT / name
    return p2 if p2.exists() else None

def test_build_parser_exists():
    p = cli.build_parser()
    assert p is not None

def test_cli_main_ramp_ss(tmp_path: pathlib.Path):
    argv = ["--root", str(tmp_path), "ramp-ss",
            "--A", "0 1; -1 -1", "--B", "0; 1", "--C", "1 0", "--D", "0",
            "--tfinal", "0.5", "--dt", "0.05"]
    rc = cli.main(argv)
    assert rc == 0
    target = _pick(tmp_path, "ramp_ss.json")
    assert target is not None, f"missing ramp_ss.json (checked {tmp_path/'out'} and {PKG_OUT})"

def test_cli_main_lsim_tf(tmp_path: pathlib.Path):
    argv = ["--root", str(tmp_path), "lsim-tf",
            "--num", "2 1", "--den", "1 1 1", "--input", "ramp",
            "--tfinal", "0.5", "--dt", "0.05"]
    rc = cli.main(argv)
    assert rc == 0
    target = _pick(tmp_path, "lsim_tf_ramp.json")
    assert target is not None, f"missing lsim_tf_ramp.json"

def test_cli_main_step_ss(tmp_path: pathlib.Path):
    argv = ["--root", str(tmp_path), "step-ss",
            "--A", "-1 -1; 6.5 0", "--B", "1 1; 1 0", "--C", "1 0; 0 1", "--D", "0 0; 0 0",
            "--input-index", "0", "--tfinal", "0.5", "--dt", "0.05", "--save-prefix", "cov_run_u"]
    rc = cli.main(argv)
    assert rc == 0
    target = _pick(tmp_path, "cov_run_u1.json")
    assert target is not None, "missing cov_run_u1.json"

def test_cli_main_second_order_single(tmp_path: pathlib.Path):
    argv = ["--root", str(tmp_path), "second-order",
            "--wn", "5", "--zeta", "0.4", "--tfinal", "0.4", "--dt", "0.01",
            "--save-prefix", "cov_so"]
    rc = cli.main(argv); assert rc == 0
    target = _pick(tmp_path, "cov_so_single.json")
    assert target is not None, "missing cov_so_single.json"

def test_cli_main_second_order_sweep(tmp_path: pathlib.Path):
    argv = ["--root", str(tmp_path), "second-order",
            "--wn", "5", "--sweep-zeta", "0.0,0.5,1.0", "--tfinal", "0.4", "--dt", "0.01",
            "--save-prefix", "cov_sweep"]
    rc = cli.main(argv); assert rc == 0
    target = _pick(tmp_path, "cov_sweep_sweep.json")
    assert target is not None, "missing cov_sweep_sweep.json"

def test_cli_main_overlays_and_mesh(tmp_path: pathlib.Path):
    argv1 = ["--root", str(tmp_path), "second-order-overlays",
             "--wn", "3", "--zetas", "0,0.2,1.0", "--tfinal", "0.4", "--dt", "0.02",
             "--save-prefix", "cov_overlay"]
    assert cli.main(argv1) == 0
    t1 = _pick(tmp_path, "cov_overlay_2D.json")
    assert t1 is not None, "missing cov_overlay_2D.json"

    argv2 = ["--root", str(tmp_path), "second-order-mesh",
             "--wn", "3", "--zeta-min", "0", "--zeta-max", "1", "--zeta-steps", "9",
             "--tfinal", "0.4", "--dt", "0.02",
             "--save-prefix", "cov_mesh"]
    assert cli.main(argv2) == 0
    t2 = _pick(tmp_path, "cov_mesh_3D.json")
    assert t2 is not None, "missing cov_mesh_3D.json"

def test_cli_main_plotly_json(tmp_path: pathlib.Path):
    try:
        import plotly  # noqa: F401
    except Exception:
        return
    argv = ["--root", str(tmp_path), "second-order-plotly",
            "--wn", "2", "--zeta-steps", "9", "--tfinal", "0.4", "--dt", "0.02",
            "--save-prefix", "cov_plotly"]
    rc = cli.main(argv); assert rc == 0
    t = _pick(tmp_path, "cov_plotly_plotly3D.json")
    assert t is not None, "missing cov_plotly_plotly3D.json"
