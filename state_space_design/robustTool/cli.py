#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry for the Robust tool (Ogata §10-9)

Works in two modes:
  1) From project root (preferred):  python -m state_space_design.robustTool.cli --help
  2) From inside this folder:        python cli.py --help
     (import shim below handles package imports)

Default I/O (running *inside* this robustTool folder):
  * Inputs : in/
  * Outputs: out/
"""
from __future__ import annotations

# ---------- Import shim so `python cli.py` works with relative imports ----------
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    import os, sys
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from state_space_design.robustTool.apis import RunRequest
    from state_space_design.robustTool.app import RobustApp
    from state_space_design.robustTool.io import save_json  # writes under package out/
else:
    # Normal package execution
    from .apis import RunRequest
    from .app import RobustApp
    from .io import save_json

import argparse
import logging as log
import os

# When running from *inside* robustTool/, write artifacts to ./out by default
OUT_DIR = "out"


def _normalize_argv(argv: list[str] | None) -> list[str] | None:
    """
    Normalize argv to be resilient to values that *start with '-'* (Oh My Zsh quirks).
    Strategy: for known string options that expect a value, if the next token
    begins with '-', attach it using the '--opt=value' form.
    """
    if argv is None:
        return None
    expects_value = {
        "--num", "--den",
        "--pid", "--K_num", "--K_den",
        "--Wm_num", "--Wm_den",
        "--Ws_num", "--Ws_den",
        "--Wa_num", "--Wa_den",
        "--export-json",
    }
    out: list[str] = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok in expects_value and (i + 1) < len(argv):
            nxt = argv[i + 1]
            if nxt.startswith("-") and not nxt.replace("-", "").isdigit():
                # attach as --opt=value to avoid argparse thinking it's a flag
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out


def _ensure_prefix_dir(path: str | None) -> str | None:
    """
    If a path is given without a directory, place it under OUT_DIR (local folder).
    Returns normalized path (and ensures directory exists).
    """
    if not path:
        return None
    dname = os.path.dirname(path)
    if not dname:
        os.makedirs(OUT_DIR, exist_ok=True)
        return os.path.join(OUT_DIR, path)
    os.makedirs(dname, exist_ok=True)
    return path


def main(argv=None):
    argv = _normalize_argv(list(argv) if argv is not None else None)

    p = argparse.ArgumentParser(
        prog="state_space_design.robustTool",
        description="Robust control sweeps (Ogata §10-9).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    # plant
    p.add_argument("--num", required=True, help='Plant numerator coeffs: e.g. "10 20"')
    p.add_argument("--den", required=True, help='Plant denominator coeffs: e.g. "1 10 24 0"')
    # controller
    p.add_argument("--pid", default=None, help="kp,ki,kd[,nd]")
    p.add_argument("--K_num", default=None); p.add_argument("--K_den", default=None)
    # weights
    p.add_argument("--Wm_num", default=None); p.add_argument("--Wm_den", default=None)
    p.add_argument("--Ws_num", default=None); p.add_argument("--Ws_den", default=None)
    p.add_argument("--Wa_num", default=None); p.add_argument("--Wa_den", default=None)
    # sweep/grid
    p.add_argument("--wmin", type=float, default=1e-2)
    p.add_argument("--wmax", type=float, default=1e2)
    p.add_argument("--npts", type=int, default=400)
    # step
    p.add_argument("--step", action="store_true")
    p.add_argument("--tfinal", type=float, default=8.0)
    p.add_argument("--dt", type=float, default=0.01)
    # plots
    p.add_argument("--plots", choices=["mpl","plotly","both","none"], default="mpl")
    # io
    p.add_argument("--export-json", default=None,
                   help="If a basename is provided, the file is saved under ./out/. "
                        "If a directory is included, it is used as-is.")
    p.add_argument("--loglevel", choices=["DEBUG","INFO","WARNING","ERROR"], default="INFO")

    args = p.parse_args(argv)
    log.basicConfig(level=getattr(log, args.loglevel), format="%(levelname)s: %(message)s")

    req = RunRequest(**vars(args))
    app = RobustApp()
    res = app.run(req)

    # Export JSON: if a directory is present, write directly; otherwise, store under package out/ via save_json.
    if args.export_json:
        if os.path.dirname(args.export_json):
            # direct write to given path
            d = os.path.dirname(args.export_json)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            with open(args.export_json, "w", encoding="utf-8") as f:
                import json
                f.write(json.dumps(res.to_jsonable(), indent=2))
            print(f"Saved JSON → {args.export_json}")
        else:
            # hand off to package writer (writes under state_space_design/robustTool/out/)
            out = save_json(res.to_jsonable(), args.export_json)
            print(f"Saved JSON → {out}")


if __name__ == "__main__":
    main()
