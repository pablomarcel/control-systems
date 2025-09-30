# transientAnalysis/responseTool/tests/test_cli_second_order_surfaces.py
from __future__ import annotations

import json
import os
import sys
from glob import glob
from pathlib import Path
from typing import Iterable, List


# ---------- helpers (project out dir, not tmp) ----------

def project_out_dir() -> Path:
    """
    Return the package out directory:
      <repo>/transientAnalysis/responseTool/out
    """
    here = Path(__file__).resolve()
    response_tool_dir = here.parents[1]            # .../transientAnalysis/responseTool
    out_dir = response_tool_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def run_cmd(args: List[str]) -> tuple[int, str]:
    """Run the CLI as a module in project context, return (exit_code, combined_output)."""
    cmd = [sys.executable, "-m", "transientAnalysis.responseTool.cli"] + args
    from subprocess import run, PIPE, STDOUT
    proc = run(cmd, stdout=PIPE, stderr=STDOUT, text=True)
    return proc.returncode, proc.stdout or ""


def remove_all(patterns: Iterable[str]) -> None:
    """Delete any existing files matching patterns in the out dir."""
    out_dir = project_out_dir()
    for pat in patterns:
        for p in out_dir.glob(pat):
            try:
                p.unlink()
            except Exception:
                pass


def one_file(pattern: str) -> Path:
    """Find exactly one file in out dir matching pattern (glob), return Path."""
    out_dir = project_out_dir()
    matches = [Path(p) for p in glob(str(out_dir / pattern))]
    assert matches, f"no files matching {pattern} in {out_dir}.\nFound: {list(out_dir.glob('*'))}"
    assert len(matches) == 1, f"expected one match for {pattern}, got {matches}"
    return matches[0]


def one_of_patterns(patterns: List[str]) -> Path:
    """Return the first found file in out dir matching any of the patterns."""
    out_dir = project_out_dir()
    for pat in patterns:
        matches = [Path(p) for p in glob(str(out_dir / pat))]
        if matches:
            assert len(matches) == 1, f"expected one match for {pat}, got {matches}"
            return matches[0]
    raise AssertionError(
        f"no files matching any of {patterns} in {out_dir}.\nFound: {list(out_dir.glob('*'))}"
    )


# ---------- tests ----------

def test_overlays_json_and_png():
    save_prefix = "ovr"
    zetas = [0.0, 0.3, 0.6, 1.0]
    zetas_arg = ",".join(str(z) for z in zetas)

    # Clean any leftovers so wildcard assertions are deterministic
    remove_all([f"{save_prefix}*_2D.*"])

    code, out = run_cmd([
        "second-order-overlays",
        "--wn", "5", "--zetas", zetas_arg,
        "--tfinal", "2", "--dt", "0.01",
        "--save-prefix", save_prefix,
        "--plot",
    ])
    assert code == 0, f"CLI failed:\n{out}"

    jpath = one_file(f"{save_prefix}*_2D.json")
    ppath = one_file(f"{save_prefix}*_2D.png")
    assert jpath.exists(), f"missing {jpath}"
    assert ppath.exists(), f"missing {ppath}"

    data = json.loads(jpath.read_text())

    # Must at least have these keys
    required = {"wn", "T", "curves"}
    assert required.issubset(data.keys()), f"missing keys in overlays JSON. Got: {sorted(data.keys())}"

    # Curves should carry zeta per-curve; build set and compare
    assert isinstance(data["curves"], list) and data["curves"], "curves must be a non-empty list"
    zetas_found = [float(c["zeta"]) for c in data["curves"] if "zeta" in c]
    assert zetas_found, "each curve should have a 'zeta' field"
    assert set(round(z, 6) for z in zetas_found) == set(round(z, 6) for z in zetas), \
        f"zetas in curves {zetas_found} != expected {zetas}"


def test_mesh_json_and_pngs():
    save_prefix = "mesh"
    zeta_min, zeta_max, zeta_steps = 0.0, 1.0, 21

    # Clean leftovers
    remove_all([f"{save_prefix}*_3D.*", f"{save_prefix}*heatmap.png"])

    code, out = run_cmd([
        "second-order-mesh",
        "--wn", "3",
        "--zeta-min", str(zeta_min),
        "--zeta-max", str(zeta_max),
        "--zeta-steps", str(zeta_steps),
        "--tfinal", "3", "--dt", "0.01",
        "--save-prefix", save_prefix,
        "--plot",
    ])
    assert code == 0, f"CLI failed:\n{out}"

    jpath = one_file(f"{save_prefix}*_3D.json")
    p3d  = one_file(f"{save_prefix}*_3D.png")
    heat = one_of_patterns([
        f"{save_prefix}*_3D_heatmap.png",   # some variants
        f"{save_prefix}*heatmap.png",       # current app file name
    ])

    assert jpath.exists(), f"missing {jpath}"
    assert p3d.exists(), f"missing {p3d}"
    assert heat.exists(), f"missing {heat}"

    data = json.loads(jpath.read_text())
    required = {"wn", "T", "zeta_grid", "Z"}
    assert required.issubset(data.keys()), f"missing keys in mesh JSON. Got: {sorted(data.keys())}"
    Nt = len(data["T"])
    Nz = len(data["zeta_grid"])
    assert isinstance(data["Z"], list) and len(data["Z"]) == Nz, "Z rows must match len(zeta_grid)"
    assert all(len(row) == Nt for row in data["Z"]), "each Z row must match len(T)"
