#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli.py — CLI entrypoint for regulatorTool.
Usage:
    python -m stateSpaceDesign.regulatorTool.cli --help
"""

from __future__ import annotations
import argparse, logging, sys, numpy as np
from .utils import parse_real_vec, parse_complex_list
from .apis import RegulatorRunRequest
from .app import run_app

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="regulatorTool",
        description="Ogata §10-6 regulator with MINIMUM-ORDER observer (SISO).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=False)

    ap.add_argument("--num", required=True, help='Plant numerator, e.g. "10 20"')
    ap.add_argument("--den", required=True, help='Plant denominator, e.g. "1 10 24 0"')
    ap.add_argument("--K_poles", default=None, help='Controller poles, e.g. "-1+2j,-1-2j,-5"')
    ap.add_argument("--obs_poles", default=None, help='Observer poles, e.g. "-4.5,-4.5"')

    ap.add_argument("--ts", type=float, default=None, help="Settling time target (sec)")
    ap.add_argument("--undershoot", default=None, help='"low,high" undershoot (e.g. "0.25,0.35")')
    ap.add_argument("--obs_speed_factor", type=float, default=5.0)

    ap.add_argument("--x0", default=None, help='Initial x, e.g. "1 0 0"')
    ap.add_argument("--e0", default=None, help='Initial e, e.g. "1 0"')
    ap.add_argument("--t_final", type=float, default=8.0)
    ap.add_argument("--dt", type=float, default=0.01)

    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--plots", choices=["none", "mpl", "plotly", "both"], default="both")
    ap.add_argument("--save_prefix", default=None)
    ap.add_argument("--export_json", default=None)

    ap.add_argument("--rl_axes", default="-14,2,-8,8", help='"xmin,xmax,ymin,ymax" for root locus')
    ap.add_argument("--rl_k", default="auto", help='kmin,kmax,samples (e.g. "1e-6,1e6,1600") or "auto"')

    ap.add_argument("--ply_width", type=int, default=0)  # 0 = autosize (responsive)
    ap.add_argument("--verbose", action="store_true")
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

    req = RegulatorRunRequest(
        num=num, den=den, K_poles=K_poles, obs_poles=obs_poles, ts=args.ts,
        undershoot=undershoot, obs_speed_factor=args.obs_speed_factor,
        x0=x0, e0=e0, t_final=args.t_final, dt=args.dt,
        rl_axes=rl_axes, rl_k=args.rl_k, pretty=args.pretty, plots=args.plots,
        save_prefix=args.save_prefix, export_json=args.export_json,
        ply_width=args.ply_width, verbose=args.verbose
    )
    run_app(req)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
