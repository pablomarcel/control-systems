#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry for the Regulator tool (Ogata §10-6, minimum-order observer)

Works in two modes:
  1) From project root (preferred):  python -m stateSpaceDesign.regulatorTool.cli --help
  2) From inside this folder:        python cli.py --help
     (import shim below handles package imports)

Default I/O when running *inside* regulatorTool/:
  * Inputs : in/
  * Outputs: out/
"""
from __future__ import annotations

# ---------- Import shim so `python cli.py` works with relative imports ----------
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    import os, sys
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from stateSpaceDesign.regulatorTool.utils import parse_real_vec, parse_complex_list
    from stateSpaceDesign.regulatorTool.apis import RegulatorRunRequest
    from stateSpaceDesign.regulatorTool.app import run_app
else:
    # Normal package execution
    from .utils import parse_real_vec, parse_complex_list
    from .apis import RegulatorRunRequest
    from .app import run_app

import argparse
import logging
import numpy as np
import os

# When running from *inside* regulatorTool/, write artifacts to ./out by default.
OUT_DIR = "out"


def _ensure_prefix_dir(prefix: str | None) -> str | None:
    """
    If a save prefix is provided without a directory, put it under OUT_DIR.
    Examples:
      - 'run1'     -> 'out/run1'   (ensures 'out/' exists)
      - 'figs/run' -> 'figs/run'   (ensures 'figs/' exists)
      - None       -> None
    """
    if not prefix:
        return None
    dname = os.path.dirname(prefix)
    if not dname:
        os.makedirs(OUT_DIR, exist_ok=True)
        return os.path.join(OUT_DIR, prefix)
    os.makedirs(dname, exist_ok=True)
    return prefix


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.regulatorTool",
        description="Ogata §10-6 regulator with MINIMUM-ORDER observer (SISO).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=False)

    ap.add_argument("--num", required=True, help='Plant numerator, e.g. "10 20"')
    ap.add_argument("--den", required=True, help='Plant denominator, e.g. "1 10 24 0"')
    ap.add_argument("--K_poles", default=None, help="Controller poles, e.g. '-1+2j,-1-2j,-5' (use quotes)")
    ap.add_argument("--obs_poles", default=None, help="Observer poles, e.g. '-4.5,-4.5' (use quotes)")

    ap.add_argument("--ts", type=float, default=None, help="Settling time target (sec)")
    ap.add_argument("--undershoot", default=None, help="'low,high' undershoot (e.g. '0.25,0.35')")
    ap.add_argument("--obs_speed_factor", type=float, default=5.0)

    ap.add_argument("--x0", default=None, help="Initial x, e.g. '1 0 0'")
    ap.add_argument("--e0", default=None, help="Initial e, e.g. '1 0'")
    ap.add_argument("--t_final", type=float, default=8.0)
    ap.add_argument("--dt", type=float, default=0.01)

    ap.add_argument("--pretty", action="store_true", help="Print SymPy ASCII pretty equations (if sympy available)")
    ap.add_argument("--plots", choices=["none", "mpl", "plotly", "both"], default="both", help="Plot backend(s)")
    ap.add_argument("--save_prefix", default=None, help="Where to save figures/html. If basename only, saved under ./out when running inside this folder.")
    ap.add_argument("--export_json", default=None, help="Write JSON summary (absolute or relative path).")

    ap.add_argument("--rl_axes", default="-14,2,-8,8", help="'xmin,xmax,ymin,ymax' for root locus")
    ap.add_argument("--rl_k", default="auto", help="kmin,kmax,samples (e.g. '1e-6,1e6,1600') or 'auto'")

    ap.add_argument("--ply_width", type=int, default=0, help="Plotly: fixed width (0 = responsive)")
    ap.add_argument("--verbose", action="store_true", help="Verbose logging")
    return ap


def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
                        format="INFO: %(message)s")

    num = parse_real_vec(args.num); den = parse_real_vec(args.den)
    K_poles = parse_complex_list(args.K_poles) if args.K_poles else None
    obs_poles = parse_complex_list(args.obs_poles) if args.obs_poles else None
    undershoot = tuple(float(x) for x in args.undershoot.replace(",", " ").split()) if args.undershoot else None
    rl_axes = tuple(float(x) for x in args.rl_axes.replace(",", " ").split())
    x0 = np.array([float(x) for x in args.x0.replace(",", " ").split()], float) if args.x0 else None
    e0 = np.array([float(x) for x in args.e0.replace(",", " ").split()], float) if args.e0 else None

    # Normalize save prefix to local ./out if user passed a bare basename when running in this folder
    save_prefix = _ensure_prefix_dir(args.save_prefix)

    req = RegulatorRunRequest(
        num=num, den=den, K_poles=K_poles, obs_poles=obs_poles, ts=args.ts,
        undershoot=undershoot, obs_speed_factor=args.obs_speed_factor,
        x0=x0, e0=e0, t_final=args.t_final, dt=args.dt,
        rl_axes=rl_axes, rl_k=args.rl_k, pretty=args.pretty, plots=args.plots,
        save_prefix=save_prefix, export_json=args.export_json,
        ply_width=args.ply_width, verbose=args.verbose
    )
    run_app(req)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
