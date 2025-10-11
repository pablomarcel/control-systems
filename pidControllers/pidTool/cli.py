#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Running as a script from inside pidControllers/pidTool
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    # Absolute imports now work
    from pidControllers.pidTool.core import tf_from_args, Requirements
    from pidControllers.pidTool.design import make_grids
    from pidControllers.pidTool.app import PIDDesignerApp
else:
    # Normal package execution
    from .core import tf_from_args, Requirements
    from .design import make_grids
    from .app import PIDDesignerApp

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PID design via computational optimization (OOP)")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="run a PID design search")
    # Plant
    run.add_argument("--plant-form", choices=["coeff", "poly", "zpk"], required=True)
    run.add_argument("--num", type=str); run.add_argument("--den", type=str)
    run.add_argument("--num-poly", type=str); run.add_argument("--den-poly", type=str)
    run.add_argument("--gain", type=float); run.add_argument("--zeros", type=str); run.add_argument("--poles", type=str)
    # Structure
    run.add_argument("--structure", choices=["pid", "pi", "pd", "pid_dz"], default="pid_dz")
    # PID grids
    run.add_argument("--Kp-vals", type=str); run.add_argument("--Ki-vals", type=str); run.add_argument("--Kd-vals", type=str)
    run.add_argument("--Kp-range", type=float, nargs=2); run.add_argument("--Ki-range", type=float, nargs=2); run.add_argument("--Kd-range", type=float, nargs=2)
    run.add_argument("--Kp-n", type=int); run.add_argument("--Ki-n", type=int); run.add_argument("--Kd-n", type=int)
    # PI grids
    run.add_argument("--pi-Kp-vals", type=str); run.add_argument("--pi-Ki-vals", type=str)
    run.add_argument("--pi-Kp-range", type=float, nargs=2); run.add_argument("--pi-Ki-range", type=float, nargs=2)
    run.add_argument("--pi-Kp-n", type=int); run.add_argument("--pi-Ki-n", type=int)
    # PD grids
    run.add_argument("--pd-Kp-vals", type=str); run.add_argument("--pd-Kd-vals", type=str)
    run.add_argument("--pd-Kp-range", type=float, nargs=2); run.add_argument("--pd-Kd-range", type=float, nargs=2)
    run.add_argument("--pd-Kp-n", type=int); run.add_argument("--pd-Kd-n", type=int)
    # Double-zero grids
    run.add_argument("--K-vals", type=str); run.add_argument("--a-vals", type=str)
    run.add_argument("--K-range", type=float, nargs=2); run.add_argument("--a-range", type=float, nargs=2)
    run.add_argument("--K-n", type=int); run.add_argument("--a-n", type=int)
    # Requirements
    run.add_argument("--max-overshoot", type=float)
    run.add_argument("--max-settling", type=float)
    run.add_argument("--max-rise", type=float)
    run.add_argument("--max-ess", type=float)
    run.add_argument("--settle-tol", type=float, default=0.02)
    # Objective
    run.add_argument("--objective", choices=["itae", "ise", "ts", "mp", "weighted"], default="itae")
    run.add_argument("--w-ts", type=float, default=1.0); run.add_argument("--w-mp", type=float, default=0.1)
    run.add_argument("--w-itae", type=float, default=1.0); run.add_argument("--w-ise", type=float, default=0.0)
    # Simulation
    run.add_argument("--tfinal", type=float); run.add_argument("--dt", type=float)
    # Outputs
    run.add_argument("--backend", choices=["mpl", "plotly", "none"], default="plotly")
    run.add_argument("--plot-top", type=int, default=5)
    run.add_argument("--no-plot", action="store_true")
    run.add_argument("--save-prefix", type=str, default="design")
    run.add_argument("--export-json", action="store_true")
    run.add_argument("--export-csv", action="store_true")
    return p

def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    if args.cmd == "run":
        Gp = tf_from_args(args)
        grids = make_grids(args)
        req = Requirements(max_overshoot=args.max_overshoot,
                           max_settling=args.max_settling,
                           max_rise=args.max_rise,
                           max_ess=args.max_ess,
                           settle_tol=args.settle_tol)
        app = PIDDesignerApp(out_dir=None)
        backend = "none" if args.no_plot else args.backend
        app.run(Gp=Gp, structure=args.structure, req=req, grids=grids,
                objective=args.objective, weights=(args.w_ts, args.w_mp, args.w_itae, args.w_ise),
                tfinal=args.tfinal, dt=args.dt, backend=backend, plot_top=args.plot_top,
                save_prefix=args.save_prefix, export_json=args.export_json, export_csv=args.export_csv)

if __name__ == "__main__":
    main()
