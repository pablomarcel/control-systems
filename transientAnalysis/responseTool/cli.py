# transientAnalysis/responseTool/cli.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
import numpy as np

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    # Absolute imports when executed as a script
    from transientAnalysis.responseTool.utils import parse_matrix, parse_vector
    from transientAnalysis.responseTool.app import ResponseToolApp
else:
    # Normal package imports
    from .utils import parse_matrix, parse_vector
    from .app import ResponseToolApp


def parse_zetas_list(s: str | None) -> list[float]:
    """Parse comma/space-separated zeta list. If empty/None, return a sensible default grid."""
    if not s:
        return [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    toks = [t for t in s.replace(",", " ").split() if t.strip()]
    return [float(t) for t in toks]


def parse_overlay_list(s: str | None) -> list[float]:
    """Like parse_zetas_list but empty/None returns [] (used for Plotly overlays)."""
    if not s:
        return []
    toks = [t for t in s.replace(",", " ").split() if t.strip()]
    return [float(t) for t in toks]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "ResponseTool — unit ramp (SS), arbitrary input (TF), "
            "MIMO SS step, and 2nd-order explorer (2D overlays / 3D mesh / Plotly 3D)"
        ),
        conflict_handler="resolve",
    )

    # Top-level --root (works when placed before the subcommand)
    p.add_argument(
        "--root",
        default=None,
        help="I/O root. Default: transientAnalysis/responseTool (the package dir).",
    )

    # Subparser parent that DOES NOT overwrite top-level --root unless explicitly passed
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        default=argparse.SUPPRESS,  # do not clobber top-level --root with None
        help="I/O root. Default: transientAnalysis/responseTool (the package dir).",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    # A) Unit-ramp via augmentation (state space)
    pA = sub.add_parser(
        "ramp-ss", parents=[common],
        help="Unit-ramp response via augmentation (state space)"
    )
    pA.add_argument("--A", type=str, default="0 1; -1 -1")
    pA.add_argument("--B", type=str, default="0; 1")
    pA.add_argument("--C", type=str, default="1 0")
    pA.add_argument("--D", type=str, default="0")
    pA.add_argument("--tfinal", type=float, default=10.0)
    pA.add_argument("--dt", type=float, default=0.01)
    pA.add_argument("--plot", action="store_true", help="show and save plot")

    # B) Arbitrary input for a transfer function
    pB = sub.add_parser(
        "lsim-tf", parents=[common],
        help="Arbitrary input for a transfer function"
    )
    pB.add_argument("--num", type=str, default="2 1", help="numerator (descending powers)")
    pB.add_argument("--den", type=str, default="1 1 1", help="denominator (descending powers)")
    pB.add_argument("--input", choices=["ramp", "sine", "square"], default="ramp")
    pB.add_argument("--tfinal", type=float, default=10.0)
    pB.add_argument("--dt", type=float, default=0.01)
    pB.add_argument("--plot", action="store_true", help="show and save plot")

    # C) MIMO state-space step from a selected input
    pC = sub.add_parser(
        "step-ss", parents=[common],
        help="MIMO state-space step from a selected input"
    )
    pC.add_argument("--A", type=str, default="-1 -1; 6.5 0")
    pC.add_argument("--B", type=str, default="1 1; 1 0")
    pC.add_argument("--C", type=str, default="1 0; 0 1")
    pC.add_argument("--D", type=str, default="0 0; 0 0")
    pC.add_argument("--input-index", type=int, default=0, help="0-based input channel index")
    pC.add_argument("--tfinal", type=float, default=10.0)
    pC.add_argument("--dt", type=float, default=0.01)
    pC.add_argument("--plot", action="store_true", help="show and save plots")
    pC.add_argument("--states", action="store_true", help="also export states via forced_response")
    pC.add_argument("--metrics", action="store_true", help="export basic step metrics (ss2tf + step_info)")
    pC.add_argument(
        "--save-prefix", type=str, default="ex5_3_from_u",
        help="filename prefix for step outputs (default: ex5_3_from_u)"
    )
    pC.add_argument(
        "--states-name", type=str, default="ex5_3_states_u",
        help="filename prefix for states outputs (default: ex5_3_states_u)"
    )

    # D) Second-order explorer (single or sweep)
    pD = sub.add_parser(
        "second-order", parents=[common],
        help="Standard 2nd-order (single response or ζ-sweep)"
    )
    # Mode A: standard parameters
    pD.add_argument("--wn", type=float, default=None, help="Natural frequency ωn [rad/s]")
    pD.add_argument("--zeta", type=float, default=None, help="Damping ratio ζ")
    pD.add_argument("--K", type=float, default=None, help="Numerator gain K (default wn^2)")
    # Mode B: coefficients tuple (K, a2, a1, a0)
    pD.add_argument(
        "--coeffs", type=float, nargs=4, metavar=("K", "a2", "a1", "a0"),
        help="Alternative: provide (K, a2, a1, a0) instead of (wn, zeta, K)"
    )
    # Time + plotting + sweep
    pD.add_argument("--tfinal", type=float, default=None, help="Time horizon (auto if omitted)")
    pD.add_argument("--dt", type=float, default=1e-3, help="Sample step for plotting")
    pD.add_argument(
        "--sweep-zeta", type=str, default="",
        help="Comma list (e.g. '0.0,0.2,0.4,0.7,1.0,2.0') to overlay responses"
    )
    pD.add_argument("--plot", action="store_true", help="show and save plot(s)")
    pD.add_argument(
        "--save-prefix", type=str, default="second_order",
        help="filename prefix for outputs (default: second_order)"
    )

    # E) Second-order 2D overlays (fixed zeta list)
    pE = sub.add_parser(
        "second-order-overlays", parents=[common],
        help="2D overlays for standard 2nd-order (selected ζ values)"
    )
    pE.add_argument("--wn", type=float, default=1.0, help="Natural frequency ωn [rad/s]")
    pE.add_argument("--zetas", type=str, default=None, help="Comma/space list of ζ (e.g. '0,0.2,0.4,1.0')")
    pE.add_argument("--tfinal", type=float, default=10.0, help="Simulation final time")
    pE.add_argument("--dt", type=float, default=0.01, help="Time step")
    pE.add_argument(
        "--save-prefix", type=str, default="std2_overlays",
        help="filename prefix for outputs (default: std2_overlays)"
    )
    pE.add_argument("--plot", action="store_true", help="show and save plot")

    # F) Second-order 3D mesh surface
    pF = sub.add_parser(
        "second-order-mesh", parents=[common],
        help="3D mesh y(t, ζ) for standard 2nd-order"
    )
    pF.add_argument("--wn", type=float, default=1.0, help="Natural frequency ωn [rad/s]")
    pF.add_argument("--zeta-min", type=float, default=0.0, help="Min ζ for 3D mesh")
    pF.add_argument("--zeta-max", type=float, default=1.0, help="Max ζ for 3D mesh")
    pF.add_argument("--zeta-steps", type=int, default=41, help="Number of ζ samples for 3D mesh")
    pF.add_argument("--tfinal", type=float, default=10.0, help="Simulation final time")
    pF.add_argument("--dt", type=float, default=0.01, help="Time step")
    pF.add_argument(
        "--save-prefix", type=str, default="std2_surface",
        help="filename prefix for outputs (default: std2_surface)"
    )
    pF.add_argument("--no-heatmap", action="store_true", help="Do not render the heatmap image")
    pF.add_argument("--plotly", action="store_true", help="Attempt interactive Plotly surface (if available)")
    pF.add_argument("--plot", action="store_true", help="Render and save the 3D wireframe (requires matplotlib)")

    # G) Second-order Plotly 3D surface (interactive)
    pG = sub.add_parser(
        "second-order-plotly", parents=[common],
        help="Interactive Plotly 3D surface for standard 2nd-order system"
    )
    pG.add_argument("--wn", type=float, default=1.0, help="Natural frequency ωn (rad/s)")
    pG.add_argument("--zeta-min", type=float, default=0.0, help="Min ζ")
    pG.add_argument("--zeta-max", type=float, default=1.0, help="Max ζ")
    pG.add_argument("--zeta-steps", type=int, default=51, help="Number of ζ samples")
    pG.add_argument("--tfinal", type=float, default=10.0, help="Simulation horizon (s)")
    pG.add_argument("--dt", type=float, default=0.01, help="Time step (s)")
    pG.add_argument("--overlay", type=str, default="", help="Comma/space list of ζ to overlay (3D line slices)")
    pG.add_argument("--title", type=str, default="", help="Custom title suffix")
    pG.add_argument(
        "--save-prefix", type=str, default="plotly_surface",
        help="filename prefix for JSON snapshot (default: plotly_surface)"
    )
    pG.add_argument("--save-html", type=str, default="", help="relative filename under out/ for interactive HTML")
    pG.add_argument("--save-png", type=str, default="", help="relative filename under out/ for PNG (needs kaleido)")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # With SUPPRESS on subparsers, args may or may not have .root set by the subparser.
    # The top-level --root remains in args.root unless a subparser explicitly overrides it.
    root_arg = getattr(args, "root", None)
    app = ResponseToolApp(
        root=(Path(root_arg) if root_arg else None),
        show_plots=bool(getattr(args, "plot", False)),
    )

    if args.cmd == "ramp-ss":
        A = parse_matrix(args.A); B = parse_matrix(args.B)
        C = parse_matrix(args.C); D = parse_matrix(args.D)
        if D is None:
            D = np.zeros((C.shape[0], B.shape[1]))
        app.compute_unit_ramp_ss(
            A, B, C, D,
            tfinal=args.tfinal, dt=args.dt,
            title_suffix="  (Ogata §5-5)"
        )
        return 0

    if args.cmd == "lsim-tf":
        num = parse_vector(args.num); den = parse_vector(args.den)
        app.simulate_tf_input(
            num, den, u=args.input, tfinal=args.tfinal, dt=args.dt,
            title=f"Arbitrary input (TF): {args.input}"
        )
        return 0

    if args.cmd == "step-ss":
        A = parse_matrix(args.A); B = parse_matrix(args.B)
        C = parse_matrix(args.C); D = parse_matrix(args.D)
        app.step_ss_from_input(
            A, B, C, D,
            input_index=args.input_index,
            tfinal=args.tfinal,
            dt=args.dt,
            title=f"Step from input u{args.input_index+1}",
            save_prefix=args.save_prefix,
        )
        if args.states:
            app.step_ss_states(
                A, B, C, D,
                input_index=args.input_index,
                tfinal=args.tfinal,
                dt=args.dt,
                save_name=args.states_name
            )
        if args.metrics:
            app.ss_step_metrics(A, B, C, D)
        return 0

    if args.cmd == "second-order":
        # Sweep if requested
        if args.sweep_zeta.strip():
            zetas = [float(z) for z in args.sweep_zeta.split(",")]
            app.second_order_sweep(
                wn=float(args.wn if args.wn is not None else 5.0),
                zetas=zetas, tfinal=args.tfinal, dt=args.dt,
                save_prefix=args.save_prefix
            )
            return 0
        # Otherwise single run
        coeffs = tuple(args.coeffs) if args.coeffs is not None else None
        app.second_order_single(
            wn=(None if coeffs else float(args.wn) if args.wn is not None else None),
            zeta=(None if coeffs else float(args.zeta) if args.zeta is not None else None),
            K=(None if coeffs else (None if args.K is None else float(args.K))),
            coeffs=coeffs,
            tfinal=args.tfinal,
            dt=args.dt,
            save_prefix=args.save_prefix,
        )
        return 0

    if args.cmd == "second-order-overlays":
        zetas = parse_zetas_list(getattr(args, "zetas", None))
        app.second_order_overlays(
            wn=float(args.wn),
            zetas=zetas,
            tfinal=float(args.tfinal),
            dt=float(args.dt),
            save_prefix=str(args.save_prefix),
            title_suffix="",
        )
        return 0

    if args.cmd == "second-order-mesh":
        app.second_order_mesh(
            wn=float(args.wn),
            zeta_min=float(args.zeta_min),
            zeta_max=float(args.zeta_max),
            zeta_steps=int(args.zeta_steps),
            tfinal=float(args.tfinal),
            dt=float(args.dt),
            save_prefix=str(args.save_prefix),
            title_suffix="",
            plot_heatmap=(not bool(getattr(args, "no_heatmap", False))),
            plotly=bool(getattr(args, "plotly", False)),
        )
        return 0

    if args.cmd == "second-order-plotly":
        overlay = parse_overlay_list(getattr(args, "overlay", None))
        save_html = getattr(args, "save_html", "") or None
        save_png = getattr(args, "save_png", "") or None
        app.second_order_plotly_surface(
            wn=float(args.wn),
            zeta_min=float(args.zeta_min),
            zeta_max=float(args.zeta_max),
            zeta_steps=int(args.zeta_steps),
            tfinal=float(args.tfinal),
            dt=float(args.dt),
            overlay=overlay,
            title=str(getattr(args, "title", "") or ""),
            save_prefix=str(args.save_prefix),
            save_html=save_html,
            save_png=save_png,
        )
        return 0

    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
