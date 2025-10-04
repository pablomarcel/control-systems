from __future__ import annotations
import argparse
import logging
from typing import Optional
from .apis import RunOptions, AnalyzerMode
from .app import StateToolApp

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="State-Space Analysis (Ogata Ch. 9) — controllability/observability/stability.")
    g_in = p.add_argument_group("Inputs")
    g_in.add_argument("--A", type=str, help='State matrix, e.g. "0 1; 0 -2" or "[[0,1],[0,-2]]".')
    g_in.add_argument("--B", type=str, help='Input matrix, e.g. "0;1" or "[[0],[1]]".')
    g_in.add_argument("--C", type=str, help='Output matrix (needed for observability/output checks).')
    g_in.add_argument("--D", type=str, help='Feedthrough matrix (for output controllability).')

    g_tf = p.add_argument_group("Alternative SISO input (build controllable canonical A,B,C,D)")
    g_tf.add_argument("--tf", type=str, help='Rational in s, e.g. "(s+3)/(s^2+3*s+2)".')
    g_tf.add_argument("--num", type=str, help='Numerator as CSV or polynomial string.')
    g_tf.add_argument("--den", type=str, help='Denominator as CSV or polynomial string.')

    g_opt = p.add_argument_group("Options")
    g_opt.add_argument("--mode", type=str, default="all",
                       choices=[m.value for m in AnalyzerMode],
                       help="Which check(s) to run.")
    g_opt.add_argument("--pretty", action="store_true", help="Pretty Unicode matrices.")
    g_opt.add_argument("--numeric", action="store_true", help="Numeric printout for matrices.")
    g_opt.add_argument("--digits", type=int, default=8, help="Digits for numeric print.")
    g_opt.add_argument("--eps", type=float, default=0.0, help="Unstable threshold for stab/detect: Re(λ) ≥ -eps.")
    g_opt.add_argument("--export-json", type=str, help="Write a summary JSON into out/.")
    g_opt.add_argument("--log", type=str, default="INFO", help="Logging level.")
    return p

def main(argv: Optional[list[str]] = None) -> int:
    p = build_parser()
    args = p.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO),
                        format="%(levelname)s: %(message)s")

    app = StateToolApp()

    options = RunOptions(
        mode=AnalyzerMode(args.mode),
        pretty=args.pretty,
        numeric=args.numeric,
        digits=args.digits,
        eps=args.eps,
        export_json=(args.export_json if args.export_json else None),
    )

    # choose source
    if args.A and args.B:
        res = app.run_from_state(A=args.A, B=args.B, C=args.C, D=args.D, options=options)
    else:
        if not (args.tf or (args.num and args.den)):
            p.error("Provide (--A and --B) OR a SISO TF via --tf OR --num/--den.")
            return 2
        res = app.run_from_tf(tf=args.tf, num=args.num, den=args.den, options=options)

    # minimal console print (succinct, JSON-ish)
    import json
    print(json.dumps(res, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
