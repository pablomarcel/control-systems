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
        description="ResponseTool — unit ramp (SS) and arbitrary input (TF)"
    )
    # Optional root; if omitted, the app defaults to the package directory.
    p.add_argument(
        "--root",
        default=None,
        help="I/O root. Default: transientAnalysis/responseTool (the package dir).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # A) Unit-ramp via augmentation (state space)
    pA = sub.add_parser("ramp-ss", help="Unit-ramp response via augmentation (state space)")
    pA.add_argument("--A", type=str, default="0 1; -1 -1")
    pA.add_argument("--B", type=str, default="0; 1")
    pA.add_argument("--C", type=str, default="1 0")
    pA.add_argument("--D", type=str, default="0")
    pA.add_argument("--tfinal", type=float, default=10.0)
    pA.add_argument("--dt", type=float, default=0.01)
    pA.add_argument("--plot", action="store_true", help="show and save plot")

    # B) Arbitrary input for a transfer function
    pB = sub.add_parser("lsim-tf", help="Arbitrary input for a transfer function")
    pB.add_argument("--num", type=str, default="2 1", help="numerator (descending powers)")
    pB.add_argument("--den", type=str, default="1 1 1", help="denominator (descending powers)")
    pB.add_argument("--input", choices=["ramp", "sine", "square"], default="ramp")
    pB.add_argument("--tfinal", type=float, default=10.0)
    pB.add_argument("--dt", type=float, default=0.01)
    pB.add_argument("--plot", action="store_true", help="show and save plot")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = ResponseToolApp(
        root=(Path(args.root) if args.root else None),
        show_plots=bool(getattr(args, "plot", False)),
    )

    if args.cmd == "ramp-ss":
        A = parse_matrix(args.A)
        B = parse_matrix(args.B)
        C = parse_matrix(args.C)
        D = parse_matrix(args.D)
        if D is None:
            D = np.zeros((C.shape[0], B.shape[1]))
        app.compute_unit_ramp_ss(
            A, B, C, D, tfinal=args.tfinal, dt=args.dt, title_suffix="  (Ogata §5-5)"
        )
        return 0

    if args.cmd == "lsim-tf":
        num = parse_vector(args.num)
        den = parse_vector(args.den)
        app.simulate_tf_input(
            num, den, u=args.input, tfinal=args.tfinal, dt=args.dt,
            title=f"Arbitrary input (TF): {args.input}"
        )
        return 0

    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
