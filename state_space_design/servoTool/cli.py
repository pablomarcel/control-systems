#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry for the Servo tool (Ogata §10 — servo I/O models)

Works in two modes:
  1) From project root (preferred):  python -m state_space_design.servoTool.cli --help
  2) From inside this folder:        python cli.py --help
     (import shim below handles absolute imports)

Default I/O when running *inside* this folder:
  * Inputs : ./in/
  * Outputs: ./out/

Note:
  Running `python -m state_space_design.servoTool.cli` from *inside* this folder
  will fail (Python cannot locate the top-level package from a subdir). Use
  `python cli.py` when you `cd state_space_design/servoTool/`.
"""
from __future__ import annotations

import argparse
import os
from typing import Optional

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Script mode (inside the package dir): add repo root to sys.path, then import absolute
    import sys
    PKG_DIR = os.path.abspath(os.path.dirname(__file__))
    REPO_ROOT = os.path.abspath(os.path.join(PKG_DIR, "..", ".."))
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from state_space_design.servoTool.apis import RunRequest, run
else:
    # Package mode (-m from repo root): use relative imports
    from .apis import RunRequest, run

# When running *inside* the package, we want bare filenames to land here:
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")


def _ensure_out_dir() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def _maybe_prefix_outdir(name: Optional[str]) -> Optional[str]:
    """
    If a bare filename is passed (no directory part), and we're running inside the
    package (script mode), prefix it with ./out so artifacts land locally.

    In package mode (-m), the apis/io layer already writes into the package `out/`.
    """
    if not name:
        return None
    # If name already has a directory, respect it as-is.
    d = os.path.dirname(name)
    if d:
        return name

    # We're in script mode if __package__ is empty/None.
    if __package__ in (None, ""):
        _ensure_out_dir()
        return os.path.join(OUT_DIR, name)
    return name


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="state_space_design.servoTool",
        description="Servo I/O model builder (OOP refactor of servos.py)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument(
        "--data",
        required=True,
        help="Controller JSON from gain_matrix.py (mode=K or KI). "
             "Example (inside-package run): in/K_controller.json",
    )
    ap.add_argument("--C", help="Output C (needed for mode=K if not present in JSON), e.g. '1 0 0'")
    ap.add_argument("--r", type=float, default=1.0, help="Reference step amplitude")
    ap.add_argument("--k_r", type=float, default=None, help="Override prefilter for mode=K")
    ap.add_argument("--t", default="0:0.01:5", help="Time vector (e.g., '0:0.01:5' or '0,1,2')")
    ap.add_argument(
        "--save_csv",
        default=None,
        help="If basename provided during inside-package run, CSV is saved under ./out/",
    )
    ap.add_argument(
        "--export_json",
        default=None,
        help="If basename provided during inside-package run, JSON is saved under ./out/",
    )
    ap.add_argument(
        "--backend",
        choices=["none", "mpl", "plotly", "both"],
        default="none",
        help="Optional quick-look plotting",
    )
    ap.add_argument("--no_show", action="store_true", help="Do not pop up windows")
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)

    # Normalize save targets for inside-package script mode
    export_json = _maybe_prefix_outdir(args.export_json)
    save_csv = _maybe_prefix_outdir(args.save_csv)

    req = RunRequest(
        data_path=args.data,
        mode_C=args.C,
        r=args.r,
        k_r_override=args.k_r,
        t=args.t,
        save_csv=save_csv,
        export_json=export_json,
        backend=args.backend,
        no_show=args.no_show,
    )
    resp = run(req)

    # Friendly console messages
    print("\n== ServoTool results ==")
    print(f"mode: {resp.model.mode.value}, r: {resp.model.r}")
    if resp.model.k_r is not None:
        print(f"k_r: {resp.model.k_r:g}")
    if resp.model.kI is not None:
        print(f"kI: {resp.model.kI:g}")
    if resp.io_json_path:
        print(f"JSON: {resp.io_json_path}")
    if resp.csv_path:
        print(f"CSV : {resp.csv_path}")
    if resp.plot_html_path:
        print(f"Plot: {resp.plot_html_path}")


if __name__ == "__main__":
    main()
