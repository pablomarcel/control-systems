#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry for the LQR tool (Ogata §10-8)

Works in two modes:
  1) From project root (preferred):  python -m stateSpaceDesign.lqrTool.cli --help
  2) From inside this folder:        python cli.py --help
     (import shim below handles package imports)

Default I/O (running *inside* the package):
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
    from stateSpaceDesign.lqrTool.apis import LQRRunRequest
    from stateSpaceDesign.lqrTool.app import LQRApp
    from stateSpaceDesign.lqrTool.core import Simulator
    from stateSpaceDesign.lqrTool.io import parse_vector, parse_Q, parse_R
    from stateSpaceDesign.lqrTool.plotting import (
        plot_mpl_initial, plot_mpl_step,
        plot_plotly_initial, plot_plotly_step
    )
else:
    # Normal package execution
    from .apis import LQRRunRequest
    from .app import LQRApp
    from .core import Simulator
    from .io import parse_vector, parse_Q, parse_R
    from .plotting import (
        plot_mpl_initial, plot_mpl_step,
        plot_plotly_initial, plot_plotly_step
    )

import argparse
import json
import os
import numpy as np


# When running from *inside* lqrTool/, write artifacts to ./out by default.
OUT_DIR = "out"


def _normalize_argv(argv: list[str] | None) -> list[str] | None:
    """
    Hook to normalize argv if we later add flags whose *values* can start with '-'.
    Currently a no-op; kept for parity with other tools.
    """
    return argv


def _ensure_prefix_dir(prefix: str | None) -> str | None:
    """
    If a save prefix is provided without a directory, put it under OUT_DIR.
    """
    if not prefix:
        return None
    dname = os.path.dirname(prefix)
    if not dname:
        os.makedirs(OUT_DIR, exist_ok=True)
        return os.path.join(OUT_DIR, prefix)
    os.makedirs(dname, exist_ok=True)
    return prefix


def _json_default(o):
    """
    Robust JSON fallback:
      - numpy scalar -> Python scalar
      - complex -> [real, imag]
    """
    try:
        import numpy as _np
        if isinstance(o, _np.generic):
            return o.item()
    except Exception:
        pass
    if isinstance(o, complex):
        return [float(o.real), float(o.imag)]
    # Let json raise for anything else
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def main(argv=None):
    argv = _normalize_argv(list(argv) if argv is not None else None)

    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.lqrTool",
        description="LQR design + simulations (Ogata §10-8) — object-oriented tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )

    # System (two alternative paths)
    g_sys = ap.add_argument_group("System definition")
    g_sys.add_argument("--A", type=str, help='State matrix, e.g. "0 1; 0 -1"')
    g_sys.add_argument("--B", type=str, help='Input matrix, e.g. "0; 1"')
    g_sys.add_argument("--C", type=str, help='Output matrix (default: y = x1)')
    g_sys.add_argument("--D", type=str, default="0", help="Direct term")
    g_sys.add_argument("--num", type=str, help='TF numerator "1, 2"')
    g_sys.add_argument("--den", type=str, help='TF denominator "1, 3, 2"')

    # Weights
    g_w = ap.add_argument_group("Weights (Q, R)")
    g_w.add_argument("--Q", type=str, default="eye",
                     help='Q: "eye", "eye:n", "diag:q1,q2,…", or matrix string')
    g_w.add_argument("--R", type=str, default="1",
                     help='R: scalar "1" (SISO) or matrix string (m×m for MIMO)')

    # Simulations
    g_s = ap.add_argument_group("Simulations")
    g_s.add_argument("--x0", type=str, default=None, help='Initial state, e.g. "1 1"')
    g_s.add_argument("--step", action="store_true", help="Unit-step tracking simulation")
    g_s.add_argument("--step_amp", type=float, default=1.0, help="Step amplitude")
    g_s.add_argument("--prefilter", type=str, default="dcgain",
                     choices=["ogata", "dcgain", "none"],
                     help="Servo prefilter mode")
    g_s.add_argument("--tfinal", type=float, default=8.0, help="Simulation length (s)")
    g_s.add_argument("--dt", type=float, default=0.01, help="Time step (s)")

    # Output & plotting
    g_o = ap.add_argument_group("Output")
    g_o.add_argument("--plots", type=str, default="mpl",
                     choices=["mpl", "plotly", "both", "none"],
                     help="Plot backend")
    g_o.add_argument("--export_json", type=str, default=None,
                     help="Path to write JSON with K, P, eigs, prefilter_gain, rank_ctrb")
    g_o.add_argument("--save_prefix", type=str, default=None,
                     help="Prefix for plot files (e.g., 'out/run1'). "
                          "If only a basename is provided, files are stored under OUT_DIR.")
    g_o.add_argument("--no_show", action="store_true", help="Do not display interactive windows")

    args = ap.parse_args(argv)

    # Build request and run app
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

    # Normalize save prefix (ensure directory exists)
    save_prefix = _ensure_prefix_dir(args.save_prefix)

    # Initial-condition response (if requested)
    if x0 is not None:
        traj_ic = Simulator.initial(model, np.asarray(res.K), x0, t)
        if args.plots in ("mpl", "both"):
            fig = plot_mpl_initial(traj_ic.T, traj_ic.X, traj_ic.Y, traj_ic.U)
            if save_prefix:
                fig.savefig(f"{save_prefix}_ic.png", dpi=150)
            if not args.no_show:
                import matplotlib.pyplot as plt
                plt.show()
        if args.plots in ("plotly", "both"):
            fig = plot_plotly_initial(traj_ic.T, traj_ic.X, traj_ic.Y, traj_ic.U)
            if save_prefix:
                fig.write_html(f"{save_prefix}_ic.html", include_plotlyjs="cdn")
            if not args.no_show:
                fig.show()

    # Step (servo) response
    if req.step:
        N = res.prefilter_gain or 0.0
        traj_st = Simulator.forced_step(model, np.asarray(res.K), float(N), t, amp=req.step_amp)
        if args.plots in ("mpl", "both"):
            fig = plot_mpl_step(traj_st.T, traj_st.X, traj_st.Y, traj_st.U)
            if save_prefix:
                fig.savefig(f"{save_prefix}_step.png", dpi=150)
            if not args.no_show:
                import matplotlib.pyplot as plt
                plt.show()
        if args.plots in ("plotly", "both"):
            fig = plot_plotly_step(traj_st.T, traj_st.X, traj_st.Y, traj_st.U)
            if save_prefix:
                fig.write_html(f"{save_prefix}_step.html", include_plotlyjs="cdn")
            if not args.no_show:
                fig.show()

    # Export JSON summary if requested (robust to complex, numpy scalars)
    if args.export_json:
        export_path = args.export_json
        dirname = os.path.dirname(export_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(res.to_jsonable(), f, indent=2, default=_json_default)

    # Always print summary to stdout (also robust)
    print(json.dumps(res.to_jsonable(), indent=2, default=_json_default))


if __name__ == "__main__":
    main()
