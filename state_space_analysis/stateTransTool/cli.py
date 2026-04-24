#!/usr/bin/env python3
from __future__ import annotations
import argparse
from .apis import StateTransRequest
from .app import run as run_app

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate the state-transition matrix Φ(t)=e^{At} from a SISO transfer function."
    )
    g_in = p.add_argument_group("Input")
    g_in.add_argument("--tf", type=str, help='Rational expression in s, e.g. "(s+3)/(s^2+3*s+2)".')
    g_in.add_argument("--num", type=str, help='Numerator as CSV "1,3" or poly "s+3".')
    g_in.add_argument("--den", type=str, help='Denominator as CSV "1,3,2" or poly "s^2+3*s+2".')
    g_in.add_argument("--example", type=str, choices=["ogata_9_1"], help="Prefill Example 9-1 TF.")

    g_opt = p.add_argument_group("Options")
    g_opt.add_argument("--canonical", default="controllable",
                       choices=["controllable", "observable", "diagonal", "jordan"],
                       help="Which A to use to generate Φ(t). Default: controllable.")
    g_opt.add_argument("--eval", type=float, dest="eval_time", help="Evaluate Φ(t) at this time (seconds).")
    g_opt.add_argument("--inverse", action="store_true", help="Also output Φ^{-1}(t) = Φ(-t).")
    g_opt.add_argument("--numeric", action="store_true", help="Print numeric (float) matrices (only with --eval).")
    g_opt.add_argument("--digits", type=int, default=8, help="Digits for numeric print.")
    g_opt.add_argument("--pretty", action="store_true", help="Unicode pretty matrices (symbolic).")
    g_opt.add_argument("--export-json", type=str, help="Write Φ(t) (and Φ^{-1}(t) if asked) to JSON.")
    g_opt.add_argument("--log", type=str, default="INFO", dest="log_level", help="Logging level (DEBUG, INFO, ...).")
    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    req = StateTransRequest(
        tf=args.tf, num=args.num, den=args.den, example=args.example,
        canonical=args.canonical, eval_time=args.eval_time, inverse=args.inverse,
        numeric=args.numeric, digits=args.digits, pretty=args.pretty,
        export_json=args.export_json, log_level=args.log_level
    )
    out = run_app(req)
    print(out)

if __name__ == "__main__":
    main()
