from __future__ import annotations
import argparse
from .apis import MinOrdRunRequest
from .app import run_app

def main():
    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.minOrdTool",
        description="Minimum-order observer (scalar output, Ogata §10-5).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument("--A", required=True, help='e.g. "0 1; -2 -3" or "[[...];[...]]"')
    ap.add_argument("--B", default=None)
    ap.add_argument("--C", required=True)
    ap.add_argument("--poles", nargs="+", required=True, help="Observer poles (n−1 values)")
    ap.add_argument("--K", default=None, help='State-feedback row, e.g. "90 29 4"')
    ap.add_argument("--K_poles", nargs="+", default=None, help="Design K via poles (n values)")
    ap.add_argument("--allow_pinv", action="store_true")
    ap.add_argument("--precision", type=int, default=4)
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--export-json", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    req = MinOrdRunRequest(
        A=args.A, B=args.B, C=args.C,
        poles=args.poles,
        K=args.K, K_poles=args.K_poles,
        allow_pinv=args.allow_pinv,
        precision=args.precision,
        pretty=args.pretty,
        export_json=args.export_json,
        verbose=args.verbose,
    )
    res = run_app(req)
    print(f"Saved JSON → {res.json_path}")

if __name__ == "__main__":
    main()
