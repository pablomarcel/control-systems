# -*- coding: utf-8 -*-
"""
CLI entry point for stateSpaceDesign.minOrdTool (Minimum-order observer, Ogata §10-5).

Works in two modes:
  1) From project root (preferred):  python -m stateSpaceDesign.minOrdTool.cli --help
  2) From inside this folder:        python cli.py --help
     (import shim enables absolute imports when __package__ is not set)

Quality-of-life:
- Robust handling of list args that start with '-' (e.g., --poles -10 -10)
  via a normalizer that coalesces all consecutive negative tokens into:
      --poles=-10,-10
  Then we split them back after argparse so downstream logic sees a clean list.
"""

from __future__ import annotations

# --- Import shim so `python cli.py` works with relative imports ---
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    import os, sys
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from stateSpaceDesign.minOrdTool.apis import MinOrdRunRequest
    from stateSpaceDesign.minOrdTool.app import run_app
else:
    # Normal package execution
    from .apis import MinOrdRunRequest
    from .app import run_app

import argparse, logging, sys


def _coalesce_negatives(argv: list[str] | None) -> list[str] | None:
    """
    Make CLI robust to values that *start with '-'* by converting sequences like:

        --poles -10 -10 --export-json out.json

    into:
        --poles=-10,-10 --export-json out.json

    We only coalesce for the sensitive options and only for tokens that begin
    with a single '-' (not '--'), stopping before the next '--option'.
    """
    if argv is None:
        return None

    sensitive = {"--poles", "--K_poles"}
    out: list[str] = []
    i = 0
    n = len(argv)

    def is_long_option(tok: str) -> bool:
        return tok.startswith("--")

    def is_negative_value(tok: str) -> bool:
        # Treat tokens starting with single '-' as negative-like values (numbers, complex, etc.)
        # but avoid '--' long options.
        return tok.startswith("-") and not tok.startswith("--")

    while i < n:
        tok = argv[i]
        if tok in sensitive:
            # Gather consecutive negative-looking tokens as values
            j = i + 1
            vals: list[str] = []
            while j < n and is_negative_value(argv[j]):
                vals.append(argv[j])
                j += 1
            if vals:
                out.append(f"{tok}=" + ",".join(vals))
                i = j
                continue
            # No negatives right after; just pass through the option
            out.append(tok)
            i += 1
            continue

        out.append(tok)
        i += 1

    return out


def _split_commas(seq: list[str] | None) -> list[str] | None:
    """Split comma-joined items (e.g., ['-10,-10']) into ['-10','-10']."""
    if not seq:
        return seq
    out: list[str] = []
    for s in seq:
        if "," in s:
            out.extend([p for p in s.replace(",", " ").split() if p])
        else:
            out.append(s)
    return out


def main(argv: list[str] | None = None) -> None:
    argv = _coalesce_negatives(list(argv) if argv is not None else sys.argv[1:])

    ap = argparse.ArgumentParser(
        prog="stateSpaceDesign.minOrdTool",
        description="Minimum-order observer (scalar output, Ogata §10-5).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument("--A", required=True, help='e.g. "0 1; -2 -3" or "[[...];[...]]"')
    ap.add_argument("--B", default=None, help='Optional input matrix, e.g. "0; 1"')
    ap.add_argument("--C", required=True, help='Output row (p=1), e.g. "1 0 0"')
    ap.add_argument(
        "--poles",
        nargs="+",
        required=True,
        help="Observer poles (n−1 values). Tip: you can also use equals-form: --poles=-10,-10",
    )
    ap.add_argument("--K", default=None, help='Optional state-feedback row, e.g. "90 29 4"')
    ap.add_argument(
        "--K_poles",
        nargs="+",
        default=None,
        help='Design K via poles (n values). Equals-form works too: --K_poles="-2+2*sqrt(3)j,-2-2*sqrt(3)j,-6"',
    )
    ap.add_argument("--allow_pinv", action="store_true", help="Use pseudoinverse if S is singular (diagnostic).")
    ap.add_argument("--precision", type=int, default=4, help="Digits for pretty-printed numeric output.")
    ap.add_argument("--pretty", action="store_true", help="Print human-readable derivations.")
    ap.add_argument("--export-json", default=None, help="Explicit JSON path; otherwise auto in stateSpaceDesign/minOrdTool/out/")
    ap.add_argument("--verbose", action="store_true", help="Verbose logging (DEBUG).")

    args = ap.parse_args(argv)
    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
                        format="%(levelname)s: %(message)s")

    # Post-parse cleanup: split comma-joined lists back into tokens
    args.poles = _split_commas(args.poles)
    if args.K_poles is not None:
        args.K_poles = _split_commas(args.K_poles)

    req = MinOrdRunRequest(
        A=args.A,
        B=args.B,
        C=args.C,
        poles=args.poles,
        K=args.K,
        K_poles=args.K_poles,
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
