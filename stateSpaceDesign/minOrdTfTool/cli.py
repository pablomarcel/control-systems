
# -*- coding: utf-8 -*-
"""
cli.py — CLI entry for minOrdTfTool (inside-package and project-root friendly)
"""
from __future__ import annotations

# Import shim for direct execution
if __package__ in (None, ""):
    import os, sys as _sys
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in _sys.path:
        _sys.path.insert(0, pkg_root)
    from stateSpaceDesign.minOrdTfTool.utils import parse_mat, split_tokens_any, parse_cplx_tokens
    from stateSpaceDesign.minOrdTfTool.app import MinOrdTfApp
else:
    from .utils import parse_mat, split_tokens_any, parse_cplx_tokens
    from .app import MinOrdTfApp

import argparse, numpy as np, sys, logging

def _normalize_negative_list_args(argv: list[str]) -> list[str] | None:
    if argv is None:
        return None
    out = []
    i = 0
    sensitive = {"--K_poles", "--poles"}
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

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.minOrdTfTool",
        description="Minimum-order observer-based controller TF (Ogata §10-5, p=1).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument("--A", required=True, help='e.g. "0 1; -2 -3"')
    ap.add_argument("--B", required=True, help='e.g. "0; 1" (single-input only)')
    ap.add_argument("--C", required=True, help='e.g. "1 0" (p=1 only)')
    ap.add_argument("--poles", nargs="+", required=True, help='Observer poles tokens (n-1 values). Supports complex tokens, use conjugate pairs overall.')
    ap.add_argument("--K", default=None, help='Explicit state-feedback row, e.g. "90 29 4"')
    ap.add_argument("--K_poles", default=None, nargs="+", help='Design K via poles, e.g. "-4" "-6" or "-4,-6"')
    ap.add_argument("--allow_pinv", action="store_true", help="If S is singular, use pseudoinverse for Ke (diagnostic).")
    ap.add_argument("--precision", type=int, default=6)
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--export_json", default=None, help='Path like "out/run.json" (relative to this folder).')
    ap.add_argument("--log", default="INFO", choices=["CRITICAL","ERROR","WARNING","INFO","DEBUG"])
    ap.add_argument("--version", action="store_true", help="Print version info and exit.")
    return ap

def _echo_version() -> None:
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            v = version("modernControl")
        except PackageNotFoundError:
            v = "0.0.0+local"
    except Exception:
        v = "0.0.0+local"
    print(f"minOrdTfTool (modernControl) version: {v}")

def main(argv=None) -> int:
    argv = _normalize_negative_list_args(list(argv) if argv is not None else sys.argv[1:])
    ap = build_parser()
    args = ap.parse_args(argv)

    if args.version:
        _echo_version()
        return 0

    logging.basicConfig(level=getattr(logging, args.log), format="%(levelname)s: %(message)s")

    try:
        A = parse_mat(args.A); B = parse_mat(args.B); C = parse_mat(args.C)
        if C.ndim == 1: C = C.reshape(1, -1)
        obs_poles = parse_cplx_tokens(args.poles)

        K = parse_mat(args.K) if args.K else None
        K_poles_tokens = None
        if args.K_poles:
            joined = " ".join(args.K_poles) if isinstance(args.K_poles, list) else args.K_poles
            K_poles_tokens = split_tokens_any(joined) if ("," in joined) else joined.split()
    except Exception as e:
        logging.error("Failed to parse inputs: %s", e)
        return 2

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
    except Exception:
        logging.exception("minOrdTfTool failed")
        return 1

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
