
"""
cli.py — CLI entry for minOrdTfTool
Usage:
  python -m stateSpaceDesign.minOrdTfTool.cli --help
"""
from __future__ import annotations
import argparse, numpy as np, sys, logging
from .utils import parse_mat, split_tokens_any, parse_cplx_tokens
from .app import MinOrdTfApp

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.minOrdTfTool",
        description="Minimum-order observer-based controller TF (Ogata §10-5, p=1).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument("--A", required=True, help='e.g. "0 1; -2 -3"')
    ap.add_argument("--B", required=True, help='e.g. "0; 1" or "0 0; 1 0"')
    ap.add_argument("--C", required=True, help='e.g. "1 0" (p=1 only)')
    ap.add_argument("--poles", nargs="+", required=True, help='Observer poles tokens (n-1 values).')
    ap.add_argument("--K", default=None, help='Explicit state-feedback row, e.g. "90 29 4"')
    ap.add_argument("--K_poles", default=None, help='Design K via poles, e.g. "-4" "-6" or "-4,-6"')
    ap.add_argument("--allow_pinv", action="store_true", help="Use pseudoinverse if S is singular.")
    ap.add_argument("--precision", type=int, default=6)
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--export_json", default=None, help='Path like "stateSpaceDesign/minOrdTfTool/out/run.json"')
    ap.add_argument("--log", default="INFO", choices=["CRITICAL","ERROR","WARNING","INFO","DEBUG"])
    return ap

def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log), format="%(levelname)s: %(message)s")

    A = parse_mat(args.A); B = parse_mat(args.B); C = parse_mat(args.C)
    if C.ndim == 1: C = C.reshape(1, -1)

    obs_poles = parse_cplx_tokens(args.poles)

    K = parse_mat(args.K) if args.K else None
    K_poles_tokens = None
    if args.K_poles:
        K_poles_tokens = split_tokens_any(args.K_poles) if ("," in args.K_poles) else args.K_poles.split()

    app = MinOrdTfApp()
    try:
        resp = app.run(
            A=A, B=B, C=C,
            obs_poles=obs_poles,
            K=K,
            K_poles_tokens=K_poles_tokens,
            allow_pinv=args.allow_pinv,
            pretty=args.pretty,
            precision=args.precision,
            export_json=args.export_json,
        )
    except Exception as e:
        logging.exception("minOrdTfTool failed")
        return 1

    # Minimal console TF echo
    num = np.asarray(resp.tf_num, float)
    den = np.asarray(resp.tf_den, float)
    print("\nController TF  Gc(s) = U(s)/(-Y(s))")
    print("num:", [float(v) for v in num])
    print("den:", [float(v) for v in den])
    if resp.json_path:
        print(f"Saved JSON → {resp.json_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
