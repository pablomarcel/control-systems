# transientAnalysis/responseTool/cli.py
#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np

from .utils import parse_matrix, parse_vector
from .app import ResponseToolApp


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="ResponseTool — unit ramp (SS), arbitrary input (TF), MIMO SS step, and 2nd-order explorer",
        conflict_handler="resolve",
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        default=None,
        help="I/O root. Default: transientAnalysis/responseTool (the package dir).",
    )

    p.add_argument(
        "--root",
        default=None,
        help="I/O root. Default: transientAnalysis/responseTool (the package dir).",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    # A) Unit-ramp via augmentation (state space)
    pA = sub.add_parser("ramp-ss", parents=[common], help="Unit-ramp response via augmentation (state space)")
    pA.add_argument("--A", type=str, default="0 1; -1 -1")
    pA.add_argument("--B", type=str, default="0; 1")
    pA.add_argument("--C", type=str, default="1 0")
    pA.add_argument("--D", type=str, default="0")
    pA.add_argument("--tfinal", type=float, default=10.0)
    pA.add_argument("--dt", type=float, default=0.01)
    pA.add_argument("--plot", action="store_true", help="show and save plot")

    # B) Arbitrary input for a transfer function
    pB = sub.add_parser("lsim-tf", parents=[common], help="Arbitrary input for a transfer function")
    pB.add_argument("--num", type=str, default="2 1", help="numerator (descending powers)")
    pB.add_argument("--den", type=str, default="1 1 1", help="denominator (descending powers)")
    pB.add_argument("--input", choices=["ramp", "sine", "square"], default="ramp")
    pB.add_argument("--tfinal", type=float, default=10.0)
    pB.add_argument("--dt", type=float, default=0.01)
    pB.add_argument("--plot", action="store_true", help="show and save plot")

    # C) MIMO state-space step from a selected input
    pC = sub.add_parser("step-ss", parents=[common], help="MIMO state-space step from a selected input")
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
    pC.add_argument("--save-prefix", type=str, default="ex5_3_from_u",
                    help="filename prefix for step outputs (default: ex5_3_from_u)")
    pC.add_argument("--states-name", type=str, default="ex5_3_states_u",
                    help="filename prefix for states outputs (default: ex5_3_states_u)")

    # D) Second-order explorer (new)
    pD = sub.add_parser("second-order", parents=[common], help="Standard 2nd-order system explorer")
    # Mode A: standard parameters
    pD.add_argument("--wn", type=float, default=None, help="Natural frequency ωn [rad/s]")
    pD.add_argument("--zeta", type=float, default=None, help="Damping ratio ζ")
    pD.add_argument("--K", type=float, default=None, help="Numerator gain K (default wn^2)")
    # Mode B: coefficients tuple (K, a2, a1, a0)
    pD.add_argument("--coeffs", type=float, nargs=4, metavar=("K","a2","a1","a0"),
                    help="Alternative: provide (K, a2, a1, a0) instead of (wn, zeta, K)")
    # Time + plotting
    pD.add_argument("--tfinal", type=float, default=None, help="Time horizon (auto if omitted)")
    pD.add_argument("--dt", type=float, default=1e-3, help="Sample step for plotting")
    pD.add_argument("--sweep-zeta", type=str, default="",
                    help="Comma list (e.g. '0.0,0.2,0.4,0.7,1.0,2.0') to overlay responses")
    pD.add_argument("--plot", action="store_true", help="show and save plot(s)")
    pD.add_argument("--save-prefix", type=str, default="second_order",
                    help="filename prefix for outputs (default: second_order)")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = ResponseToolApp(
        root=(Path(args.root) if args.root else None),
        show_plots=bool(getattr(args, "plot", False)),
    )

    if args.cmd == "ramp-ss":
        A = parse_matrix(args.A); B = parse_matrix(args.B)
        C = parse_matrix(args.C); D = parse_matrix(args.D)
        if D is None:
            D = np.zeros((C.shape[0], B.shape[1]))
        app.compute_unit_ramp_ss(A, B, C, D, tfinal=args.tfinal, dt=args.dt, title_suffix="  (Ogata §5-5)")
        return 0

    if args.cmd == "lsim-tf":
        num = parse_vector(args.num); den = parse_vector(args.den)
        app.simulate_tf_input(num, den, u=args.input, tfinal=args.tfinal, dt=args.dt,
                              title=f"Arbitrary input (TF): {args.input}")
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
            app.step_ss_states(A, B, C, D, input_index=args.input_index, tfinal=args.tfinal, dt=args.dt,
                               save_name=args.states_name)
        if args.metrics:
            app.ss_step_metrics(A, B, C, D)
        return 0

    if args.cmd == "second-order":
        # Sweep?
        if args.sweep_zeta.strip():
            zetas = [float(z) for z in args.sweep_zeta.split(",")]
            app.second_order_sweep(wn=float(args.wn if args.wn is not None else 5.0),
                                   zetas=zetas, tfinal=args.tfinal, dt=args.dt,
                                   save_prefix=args.save_prefix)
            return 0
        # Single
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

    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
