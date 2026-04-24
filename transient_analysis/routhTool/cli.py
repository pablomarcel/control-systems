
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)

    # absolute imports from the package
    from transient_analysis.routhTool.app import RouthApp
else:
    # Normal package execution
    from .app import RouthApp


def _print_table(array, degrees):
    # tiny pretty printer kept local to CLI
    colw = 14
    print("\nRouth array:")
    for deg, row in zip(degrees, array):
        cells = " ".join(f"{c:>{colw}}" for c in row)
        print(f"s^{deg:>2} | {cells}")


def cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Routh array builder (numeric + symbolic).")
    ap.add_argument("--coeffs", required=True,
                    help="a0,a1,...,an in descending powers (e.g. '1,5,6,K').")
    ap.add_argument("--symbol", action="append", default=[],
                    help="Symbolic parameter name(s), repeatable.")
    ap.add_argument("--solve-for", default=None, help="Solve first-column > 0 for this single symbol.")
    ap.add_argument("--eps", type=float, default=1e-9, help="Small epsilon for ε-trick.")
    ap.add_argument("--verify", action="store_true", help="If numeric, verify by numpy.roots.")
    ap.add_argument("--hurwitz", action="store_true", help="Compute Hurwitz leading minors (SymPy).")
    ap.add_argument("--export", default=None, help="Basename to export JSON to out/<basename>.json")
    args = ap.parse_args(argv)

    # package dir inferred from this file
    pkg_dir = Path(__file__).resolve().parent
    app = RouthApp.discover(pkg_dir)

    payload = app.run(
        args.coeffs,
        symbols=args.symbol,
        solve_for=args.solve_for,
        eps=args.eps,
        compute_hurwitz=args.hurwitz,
        verify_numeric=args.verify,
        export_basename=args.export,
    )

    _print_table(payload["routh_array"], payload["degrees"])
    print("\nFirst column:", payload["first_column"])
    print(f"\n#RHP roots by Routh (sign changes) = {payload['rhp_by_routh']}")
    if payload["rhp_by_roots"] is not None:
        print(f"#RHP roots by numpy.roots verification = {payload['rhp_by_roots']}")

    if payload["hurwitz_minors"]:
        print("\nHurwitz leading principal minors Δ1..Δn:")
        for i, d in enumerate(payload["hurwitz_minors"], 1):
            print(f"  Δ{i} = {d}")

    if payload["stability_condition"]:
        print(f"\nStability region (first-column > 0):\n  {payload['stability_condition']}")

    print("\nNotes:")
    for n in payload["notes"]:
        print("  •", n)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
