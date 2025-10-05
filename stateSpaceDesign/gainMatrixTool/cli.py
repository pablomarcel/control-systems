from __future__ import annotations
import argparse
from .app import GainMatrixApp

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.gainMatrixTool",
        description="Gain-matrix design (state feedback K, observer L, servo kI) — Ogata Ch.10",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False
    )
    sub = ap.add_subparsers(dest="cmd", required=False)

    # single
    sp = sub.add_parser("run", help="Single-case design")
    sp.add_argument("--mode", choices=["K","L","KI"], default="K")
    sp.add_argument("--A", required=True, help='Matrix A, e.g. "0 1; -2 -3"')
    sp.add_argument("--B", help='Matrix B, e.g. "0; 1" (required for K/KI)')
    sp.add_argument("--C", help='Matrix C, e.g. "1 0" (required for L/KI)')
    sp.add_argument("--poles", nargs="+", required=True, help='Desired poles, e.g. "-2+4j -2-4j -10"')
    sp.add_argument("--method", choices=["auto","acker","place"], default="auto")
    sp.add_argument("--verify", action="store_true")
    sp.add_argument("--pretty", action="store_true")
    sp.add_argument("--export_json", help="Write JSON to path")
    sp.add_argument("--log", help="Log file path")
    sp.add_argument("--verbose", action="store_true")

    # batch
    bp = sub.add_parser("batch", help="Batch from CSV or YAML")
    bp.add_argument("--csv", help="CSV file of cases")
    bp.add_argument("--yaml", help="YAML file of cases")
    bp.add_argument("--export_dir", default="stateSpaceDesign/gainMatrixTool/out_json", help="Output dir for JSON")
    bp.add_argument("--verify", action="store_true")
    bp.add_argument("--pretty", action="store_true")
    bp.add_argument("--log", help="Log file path")
    bp.add_argument("--verbose", action="store_true")

    # default to single if no subcommand
    args = ap.parse_args(argv)
    if args.cmd is None:
        ap.print_help()
        return 0

    app = GainMatrixApp.default()
    log = getattr(args, "log", None)
    verbose = getattr(args, "verbose", False)
    app.configure_logging(log, verbose)

    if args.cmd == "run":
        if args.mode in ("K","KI") and not args.B:
            sp.error("--B required for mode K/KI")
        if args.mode in ("L","KI") and not args.C:
            sp.error("--C required for mode L/KI")
        payload = app.run_single(
            mode=args.mode, A=args.A, B=args.B, C=args.C,
            poles=args.poles, method=args.method, verify=args.verify, pretty=args.pretty
        )
        if args.export_json:
            from .io import JsonExporter
            JsonExporter().export(payload, args.export_json)
    elif args.cmd == "batch":
        if not args.csv and not args.yaml:
            bp.error("Provide --csv or --yaml")
        app.run_batch(args.csv, args.yaml, args.export_dir, args.verify, args.pretty)

if __name__ == "__main__":
    main()
