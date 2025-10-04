from __future__ import annotations
import argparse
import logging
from .apis import StateRepAPIRequest
from .app import StateRepApp

def main(argv=None):
    p = argparse.ArgumentParser(
        description="stateRepTool — State-space canonical forms (controllable, observable, diagonal, Jordan)."
    )
    g_in = p.add_argument_group("Input")
    g_in.add_argument("--tf", type=str, help='Rational expression in s, e.g. "(s+3)/(s^2+3*s+2)".')
    g_in.add_argument("--num", type=str, help='Numerator as CSV "1,3" or poly "s+3".')
    g_in.add_argument("--den", type=str, help='Denominator as CSV "1,3,2" or poly "s^2+3*s+2".')
    g_in.add_argument("--example", type=str, choices=["ogata_9_1"], help="Prefill known example.")

    g_out = p.add_argument_group("Options")
    g_out.add_argument("--canonical", type=str, default="all",
                       choices=["all", "controllable", "observable", "diagonal", "jordan"])
    g_out.add_argument("--numeric", action="store_true", help="Print numeric (float) matrices.")
    g_out.add_argument("--digits", type=int, default=6, help="Digits for numeric print.")
    g_out.add_argument("--no-verify", action="store_true", help="Skip symbolic verification.")
    g_out.add_argument("--pretty", action="store_true", help="(Reserved) Pretty-print; JSON always stores exact.")
    g_out.add_argument("--export-json", type=str, help="Write results to JSON file (relative to out/).")
    g_out.add_argument("--log", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ...).")

    args = p.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO),
                        format="%(levelname)s: %(message)s")

    req = StateRepAPIRequest(
        tf=args.tf, num=args.num, den=args.den, example=args.example,
        which=args.canonical, numeric=args.numeric, digits=args.digits,
        pretty=args.pretty, verify=not args.no_verify
    )
    app = StateRepApp()
    results = app.run(req, export_json=args.export_json)

    # Human-side echo
    for name, blk in results.items():
        print(f"\n== {name.upper()} ==")
        for k in ("A","B","C","D"):
            print(f"{k} = {blk[k]}")

if __name__ == "__main__":
    main()
