#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI entry for the LQR tool.

Run from repo root:

    python -m stateSpaceDesign.lqrTool.cli --help

Default in/out:
  * Inputs:  stateSpaceDesign/lqrTool/in
  * Outputs: stateSpaceDesign/lqrTool/out
"""
from __future__ import annotations
import argparse
import json
import os
import numpy as np

from .apis import LQRRunRequest
from .app import LQRApp
from .core import Simulator
from .io import parse_vector, parse_Q, parse_R
from .plotting import (
    plot_mpl_initial, plot_mpl_step,
    plot_plotly_initial, plot_plotly_step
)

OUT_DIR = os.path.join("stateSpaceDesign", "lqrTool", "out")

def main(argv=None):
    ap = argparse.ArgumentParser(description="LQR design + simulations (Ogata §10-8) — OOP version")
    # System (two paths)
    ap.add_argument("--A", type=str, help='State matrix "a11 a12; a21 a22; ..."')
    ap.add_argument("--B", type=str, help='Input matrix "b11; b21; ..."')
    ap.add_argument("--C", type=str, help='Output matrix (default: y = x1)')
    ap.add_argument("--D", type=str, default="0", help="Direct term (default 0)")
    ap.add_argument("--num", type=str, help='TF numerator "..."')
    ap.add_argument("--den", type=str, help='TF denominator "..."')
    # Weights
    ap.add_argument("--Q", type=str, default="eye", help='Q: "eye", "eye:n", "diag:q1,q2,…", or matrix')
    ap.add_argument("--R", type=str, default="1", help='R: scalar "1" or matrix')
    # Sims
    ap.add_argument("--x0", type=str, default=None, help='Initial state "x10 x20 …"')
    ap.add_argument("--step", action="store_true", help="Unit-step tracking simulation")
    ap.add_argument("--step_amp", type=float, default=1.0)
    ap.add_argument("--prefilter", type=str, default="dcgain", choices=["ogata", "dcgain", "none"])
    ap.add_argument("--tfinal", type=float, default=8.0)
    ap.add_argument("--dt", type=float, default=0.01)
    # Output & plotting
    ap.add_argument("--plots", type=str, default="mpl", choices=["mpl", "plotly", "both", "none"])
    ap.add_argument("--export_json", type=str, default=None, help="Path to write JSON with K,P,eigs,N,rank")
    ap.add_argument("--save_prefix", type=str, default=None, help="Prefix for plot files (e.g., out/run1)")
    ap.add_argument("--no_show", action="store_true", help="Do not display interactive windows")

    args = ap.parse_args(argv)

    req = LQRRunRequest(
        A=args.A, B=args.B, C=args.C, D=args.D, num=args.num, den=args.den,
        Q=args.Q, R=args.R,
        x0=args.x0, step=bool(args.step), step_amp=args.step_amp,
        prefilter=args.prefilter, tfinal=args.tfinal, dt=args.dt, plots=args.plots
    )
    app = LQRApp(req)
    res = app.run()

    # Optional: run fresh sims for plotting/export
    model = app.build_model()
    t = np.arange(0.0, req.tfinal + 1e-12, req.dt)
    x0 = parse_vector(req.x0) if req.x0 else None

    # initial
    if x0 is not None:
        from .core import Simulator
        traj_ic = Simulator.initial(model, np.asarray(res.K), x0, t)
        if args.plots in ("mpl", "both"):
            fig = plot_mpl_initial(traj_ic.T, traj_ic.X, traj_ic.Y, traj_ic.U)
            if args.save_prefix:
                os.makedirs(os.path.dirname(args.save_prefix), exist_ok=True)
                fig.savefig(f"{args.save_prefix}_ic.png", dpi=150)
            if not args.no_show:
                import matplotlib.pyplot as plt
                plt.show()
        if args.plots in ("plotly", "both"):
            fig = plot_plotly_initial(traj_ic.T, traj_ic.X, traj_ic.Y, traj_ic.U)
            if args.save_prefix:
                os.makedirs(os.path.dirname(args.save_prefix), exist_ok=True)
                fig.write_html(f"{args.save_prefix}_ic.html", include_plotlyjs="cdn")
            if not args.no_show:
                fig.show()

    # step
    if req.step:
        N = res.prefilter_gain or 0.0
        traj_st = Simulator.forced_step(model, np.asarray(res.K), float(N), t, amp=req.step_amp)
        if args.plots in ("mpl", "both"):
            fig = plot_mpl_step(traj_st.T, traj_st.X, traj_st.Y, traj_st.U)
            if args.save_prefix:
                os.makedirs(os.path.dirname(args.save_prefix), exist_ok=True)
                fig.savefig(f"{args.save_prefix}_step.png", dpi=150)
            if not args.no_show:
                import matplotlib.pyplot as plt
                plt.show()
        if args.plots in ("plotly", "both"):
            fig = plot_plotly_step(traj_st.T, traj_st.X, traj_st.Y, traj_st.U)
            if args.save_prefix:
                os.makedirs(os.path.dirname(args.save_prefix), exist_ok=True)
                fig.write_html(f"{args.save_prefix}_step.html", include_plotlyjs="cdn")
            if not args.no_show:
                fig.show()

    if args.export_json:
        os.makedirs(os.path.dirname(args.export_json) or ".", exist_ok=True)
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump(res.to_jsonable(), f, indent=2)
    # stdout summary
    print(json.dumps(res.to_jsonable(), indent=2))

if __name__ == "__main__":
    main()
