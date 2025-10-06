# -*- coding: utf-8 -*-
"""
CLI entry point for observerGainMatrixTool.

Works in two modes:
  1) From project root (preferred):  python -m stateSpaceDesign.observerGainMatrixTool.cli --help
  2) From inside this folder:        python cli.py --help
     (we install a small import shim when __package__ is not set)
"""
from __future__ import annotations

# --- Import shim so `python cli.py` works with relative imports ---
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    import os, sys
    from pathlib import Path
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from stateSpaceDesign.observerGainMatrixTool.apis import ObserverRequest
    from stateSpaceDesign.observerGainMatrixTool.app import ObserverGainMatrixApp
    from stateSpaceDesign.observerGainMatrixTool.utils import CSV_CPLX_RE
else:
    # Normal package execution
    from .apis import ObserverRequest
    from .app import ObserverGainMatrixApp
    from .utils import CSV_CPLX_RE

import argparse, json, logging, sys, os
from pathlib import Path

# ------------------------------
# Helpers for robust CLI parsing
# ------------------------------

def _normalize_negative_list_args(argv: list[str] | None) -> list[str] | None:
    """
    Make CLI robust to values that *start with '-'* by converting:
        --K_poles <value>   ->  --K_poles=<value>
    when the next token begins with '-' (argparse would otherwise treat it as a new option).
    """
    if argv is None:
        return None
    out = []
    i = 0
    sensitive = {"--K_poles"}
    while i < len(argv):
        tok = argv[i]
        if tok in sensitive and i + 1 < len(argv):
            nxt = argv[i + 1]
            if nxt.startswith("-") and not nxt.startswith("--"):
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out

def _parser_epilog() -> str:
    return (
        "Tips:\n"
        "  • If a value starts with '-', prefer equals form, e.g. --K_poles=\"-3,-4\".\n"
        "  • Run as a module from repo root *or* as a script in this folder.\n"
        "  • --export_json path rules:\n"
        "      - Absolute or path/with/dirs: written exactly there.\n"
        "      - Bare filename: written to the current working directory.\n"
    )

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.observerGainMatrixTool",
        description="Observer Gain Matrix Tool — full-order observer Ke, optional K, TF, and zero-input sim",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
        epilog=_parser_epilog()
    )
    # Plant
    ap.add_argument("--A", required=True, help='State matrix, e.g. "0 1; -2 -3"')
    ap.add_argument("--B", default=None, help='Input matrix (needed for K/closed-loop), e.g. "0; 1"')
    ap.add_argument("--C", required=True, help='Output matrix, e.g. "1 0" or multi-row "1 0; 0 1"')
    # Observer
    ap.add_argument("--poles", nargs="+", type=complex, required=True,
                    help="Observer poles (n values). Example: -8 -8, or -10 -12, or -1.8+2.4j -1.8-2.4j")
    ap.add_argument("--method", choices=["auto","place","ack"], default="auto",
                    help="Observer synthesis method: dual place(), Ackermann, or auto")
    ap.add_argument("--place_fallback", choices=["none","ack","jitter"], default="none",
                    help="If place() multiplicities exceed p, pick a fallback strategy")
    ap.add_argument("--jitter_eps", type=float, default=1e-6, help="Jitter used when fallback=jitter")
    # Controller
    ap.add_argument("--K", type=str, default=None, help='Explicit K row, e.g. "29.6 3.6"')
    ap.add_argument("--K_poles", default=None,
                    help='Controller poles as a single quoted CSV string, e.g. "-1.8+2.4j,-1.8-2.4j" (equals-form recommended)')
    ap.add_argument("--K_poles_list", nargs="+", default=None,
                    help='Controller poles as separate tokens, e.g. "-1.8+2.4j" "-1.8-2.4j"')
    # Simulation / exports
    ap.add_argument("--compute_closed_loop", action="store_true", help="Build closed-loop augmented A, Gc(s), and optional zero-input sim")
    ap.add_argument("--x0", type=str, default=None, help='Initial x, e.g. "1,0"')
    ap.add_argument("--e0", type=str, default=None, help='Initial observer error, e.g. "0,0"')
    ap.add_argument("--t_final", type=float, default=0.0, help="Final time for zero-input sim (sec)")
    ap.add_argument("--dt", type=float, default=0.01, help="Integration step for zero-input sim (sec)")
    ap.add_argument("--pretty", action="store_true", help="Print a human-friendly summary instead of JSON")
    ap.add_argument("--equations", action="store_true", help="(reserved for future pretty expansions)")
    ap.add_argument("--eq_style", choices=["auto","ascii","numpy","both"], default="auto")
    ap.add_argument("--latex", default=None, help="Write LaTeX observer equation snippet to this filename under out/")
    ap.add_argument("--export_json", default=None, help="Write JSON to this filename (see epilog for path rules)")
    ap.add_argument("--log", default="WARNING", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return ap

def main(argv=None):
    argv = _normalize_negative_list_args(list(argv) if argv is not None else sys.argv[1:])
    ap = build_parser()
    # parse allowing unknown (to capture stray CSV after --K_poles that begins with '-')
    args, unknown = ap.parse_known_args(argv)
    logging.basicConfig(level=getattr(logging, str(args.log).upper(), logging.WARNING),
                        format="%(levelname)s: %(message)s")

    # If --K_poles missing but a CSV-looking token is present in unknowns, capture it
    if args.K_poles is None and not args.K and not args.K_poles_list:
        for tok in unknown:
            if CSV_CPLX_RE.match(tok):
                args.K_poles = tok
                break

    req = ObserverRequest(
        A=args.A, C=args.C, poles=args.poles, method=args.method,
        place_fallback=args.place_fallback, jitter_eps=args.jitter_eps,
        B=args.B, K=args.K, K_poles_csv=args.K_poles, K_poles_list=args.K_poles_list,
        compute_closed_loop=args.compute_closed_loop, x0=args.x0, e0=args.e0,
        t_final=args.t_final, dt=args.dt, pretty=args.pretty, equations=args.equations,
        eq_style=args.eq_style, latex_out=(args.latex if args.latex else None)
    )

    app = ObserverGainMatrixApp()
    try:
        resp = app.run(req)
    except Exception as e:
        logging.error(str(e))
        return 2

    # Handle export path:
    #  - absolute or contains a path separator -> write exactly there
    #  - bare filename -> write to current working directory
    if args.export_json:
        export_path = Path(args.export_json)
        path_has_sep = (os.sep in args.export_json) or (os.altsep and os.altsep in args.export_json)
        if export_path.is_absolute() or path_has_sep:
            export_path = (Path.cwd() / export_path) if not export_path.is_absolute() else export_path
        else:
            export_path = Path.cwd() / args.export_json
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(json.dumps(resp.data, indent=2), encoding="utf-8")

    # Pretty or JSON to stdout
    if args.pretty and resp.pretty_blocks:
        print("\n".join(resp.pretty_blocks))
    else:
        print(json.dumps(resp.data, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
