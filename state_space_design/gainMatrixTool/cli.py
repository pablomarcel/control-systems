# -*- coding: utf-8 -*-
"""
CLI entry point for gainMatrixTool.

Works in two modes:
  1) From project root (preferred):  python -m state_space_design.gainMatrixTool.cli --help
  2) From inside this folder:        python cli.py --help
     (import shim enables absolute imports when __package__ is not set)
"""
from __future__ import annotations

# --- Import shim so `python cli.py` works with relative imports ---
_SCRIPT_MODE = False
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    import os, sys
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from state_space_design.gainMatrixTool.app import GainMatrixApp
    _SCRIPT_MODE = True
else:
    # Normal package execution
    from .app import GainMatrixApp

import argparse
import sys


def _normalize_negative_list_args(argv: list[str] | None) -> list[str] | None:
    """
    Make CLI robust to values that *start with '-'* for list-like options.

    For --poles specifically, fold ALL consecutive negative tokens into a single equals-form:
        --poles -2 -5 -8   ->   ["--poles=-2 -5 -8"]
    This prevents argparse from treating subsequent negatives as new options.

    Notes:
    - Argparse will pass the single folded string as one list element for '--poles' (since nargs='+'),
      which is fine: downstream we split the string ourselves.
    """
    if argv is None:
        return None

    out: list[str] = []
    i = 0
    sensitive = {"--poles"}

    while i < len(argv):
        tok = argv[i]

        if tok in sensitive and i + 1 < len(argv):
            # Collect all consecutive negative tokens after --poles
            j = i + 1
            negs: list[str] = []
            while j < len(argv):
                nxt = argv[j]
                # Stop if next looks like another long option ("--...") or a non-negative value
                if nxt.startswith("--"):
                    break
                if nxt.startswith("-"):
                    negs.append(nxt)
                    j += 1
                    continue
                # Non-negative plain value -> stop collecting (leave it for normal parsing)
                break

            if negs:
                # Fold all negatives into a single equals-form token
                out.append(f"{tok}=" + " ".join(negs))
                i = j
                continue
            # Fall through if no negatives immediately after --poles

        out.append(tok)
        i += 1

    return out


def main(argv=None):
    argv = _normalize_negative_list_args(list(argv) if argv is not None else sys.argv[1:])

    ap = argparse.ArgumentParser(
        prog="state_space_design.gainMatrixTool",
        description="Gain-matrix design (state feedback K, observer L, servo kI) — Ogata Ch.10",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    sub = ap.add_subparsers(dest="cmd", required=False)

    # single
    sp = sub.add_parser("run", help="Single-case design")
    sp.add_argument("--mode", choices=["K", "L", "KI"], default="K")
    sp.add_argument("--A", required=True, help='Matrix A, e.g. "0 1; -2 -3"')
    sp.add_argument("--B", help='Matrix B, e.g. "0; 1" (required for K/KI)')
    sp.add_argument("--C", help='Matrix C, e.g. "1 0" (required for L/KI)')
    sp.add_argument("--poles", nargs="+", required=True, help='Desired poles, e.g. "-2+4j -2-4j -10"')
    sp.add_argument("--method", choices=["auto", "acker", "place"], default="auto")
    sp.add_argument("--verify", action="store_true")
    sp.add_argument("--pretty", action="store_true")
    sp.add_argument("--export_json", help="Write JSON to path")
    sp.add_argument("--log", help="Log file path")
    sp.add_argument("--verbose", action="store_true")

    # batch
    bp = sub.add_parser("batch", help="Batch from CSV or YAML")
    bp.add_argument("--csv", help="CSV file of cases")
    bp.add_argument("--yaml", help="YAML file of cases")
    # Default export dir depends on how we're invoked (script vs package)
    default_export = "out_json" if _SCRIPT_MODE else "state_space_design/gainMatrixTool/out_json"
    bp.add_argument("--export_dir", default=default_export, help="Output dir for JSON")
    bp.add_argument("--verify", action="store_true")
    bp.add_argument("--pretty", action="store_true")
    bp.add_argument("--log", help="Log file path")
    bp.add_argument("--verbose", action="store_true")

    # default to help if no subcommand
    args = ap.parse_args(argv)
    if args.cmd is None:
        ap.print_help()
        return 0

    app = GainMatrixApp.default()
    log = getattr(args, "log", None)
    verbose = getattr(args, "verbose", False)
    app.configure_logging(log, verbose)

    if args.cmd == "run":
        if args.mode in ("K", "KI") and not args.B:
            sp.error("--B required for mode K/KI")
        if args.mode in ("L", "KI") and not args.C:
            sp.error("--C required for mode L/KI")

        payload = app.run_single(
            mode=args.mode,
            A=args.A,
            B=args.B,
            C=args.C,
            poles=args.poles,
            method=args.method,
            verify=args.verify,
            pretty=args.pretty,
        )
        if args.export_json:
            # Write JSON where the user asked for it
            if __package__ in (None, ""):
                from state_space_design.gainMatrixTool.io import JsonExporter
            else:
                from .io import JsonExporter
            JsonExporter().export(payload, args.export_json)

    elif args.cmd == "batch":
        if not args.csv and not args.yaml:
            bp.error("Provide --csv or --yaml")
        app.run_batch(args.csv, args.yaml, args.export_dir, args.verify, args.pretty)


if __name__ == "__main__":
    main()
