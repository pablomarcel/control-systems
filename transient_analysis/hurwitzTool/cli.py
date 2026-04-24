# =============================
# File: transient_analysis/hurwitzTool/cli.py
# =============================
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import sympy as sp

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from transient_analysis.hurwitzTool.apis import (
        HurwitzService,
        NumericCheckRequest,
        SymbolicRegionRequest,
        Scan1DRequest,
        Scan2DRequest,
    )
    from transient_analysis.hurwitzTool.utils import ascii_heatmap, parse_coeffs
    from transient_analysis.hurwitzTool.io import IOManager
else:
    # Normal package execution
    from .apis import (
        HurwitzService,
        NumericCheckRequest,
        SymbolicRegionRequest,
        Scan1DRequest,
        Scan2DRequest,
    )
    from .utils import ascii_heatmap, parse_coeffs
    from .io import IOManager


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Hurwitz-stability tool (OO). Numeric + symbolic, multi-parameter, scans.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument("--coeffs", required=True,
                    help="Descending coefficients 'a0, a1, ..., an' (allow symbols)")
    ap.add_argument("--symbols", default=None,
                    help="Comma-separated symbol names (auto-detect if omitted)")
    ap.add_argument("--solve-for", dest="solvefor", default=None,
                    help="Solve region for these symbols")
    ap.add_argument("--lienard", action="store_true",
                    help="Use Liénard–Chipart reduced tests (a_i>0)")
    ap.add_argument("--subs", default=None,
                    help="Numeric substitutions like 'K=3.5,alpha=2'")
    ap.add_argument("--verify", action="store_true",
                    help="Count RHP roots with numpy.roots after substitution")
    ap.add_argument("--scan", default=None, help="1-D scan: 'K:lo:hi:step'")
    ap.add_argument("--scan2", default=None, help="2-D scan: 'S1:lo:hi:ds;S2:lo:hi:ds'")
    ap.add_argument("--csv", default=None, help="CSV path for --scan")
    ap.add_argument("--csv2", default=None, help="CSV path for --scan2")
    ap.add_argument("--png", default=None, help="If --scan2, save a PNG heatmap to this path")
    ap.add_argument("--tol", type=float, default=1e-10)
    ap.add_argument("--intervals-pretty", action="store_true",
                    help="For 1-D regions: print pretty intervals and LaTeX")
    ap.add_argument("--base-dir", default=".",
                    help="Base dir for hurwitzTool (contains in/ out/)")
    return ap


def _parse_subs_arg(s: str | None) -> dict[str, float]:
    if not s:
        return {}
    out: dict[str, float] = {}
    for part in s.replace(";", ",").split(","):
        if not part.strip():
            continue
        if "=" not in part:
            raise ValueError(f"Bad --subs item '{part}', expected NAME=value")
        k, v = part.split("=", 1)
        out[k.strip()] = float(v.strip())
    return out


def _parse_scan1d_arg(scan: str) -> tuple[str, float, float, float]:
    name, lo, hi, step = [q.strip() for q in scan.replace(";", ":").split(":")]
    return name, float(lo), float(hi), float(step)


def _parse_scan2d_arg(scan2: str) -> tuple[tuple[str, float, float, float], tuple[str, float, float, float]]:
    parts = [p.strip() for p in scan2.split(";") if p.strip()]
    if len(parts) != 2:
        raise ValueError("Bad --scan2; expected 'S1:lo:hi:ds;S2:lo:hi:ds'")
    sx, xlo, xhi, dx = [q.strip() for q in parts[0].split(":")]
    sy, ylo, yhi, dy = [q.strip() for q in parts[1].split(":")]
    return (sx, float(xlo), float(xhi), float(dx)), (sy, float(ylo), float(yhi), float(dy))


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    base_dir = Path(args.base_dir).resolve()
    svc = HurwitzService(base_dir)
    iom = IOManager(base_dir)  # avoid name 'io' to not shadow stdlib module

    # Numeric path if --subs given
    if args.subs:
        subs = _parse_subs_arg(args.subs)
        res = svc.numeric_check(
            NumericCheckRequest(
                coeffs=args.coeffs,
                subs=subs,
                use_lienard=args.lienard,
                tol=args.tol,
            )
        )
        print("Used:", res.used)
        print("a (numeric) =", res.a_numeric)
        print("Δk values:")
        for i, d in enumerate(res.minors_numeric, 1):
            print(f"  Δ{i} = {d:.12g}")
        print("\nChecks:")
        print("  a0>0?", res.a0_pos)
        if args.lienard:
            print("  all coefficients > 0?", res.coeff_pos)
        print("\nHurwitz stable?", res.ok)

        if args.verify:
            # Recompute numeric coefficients and count RHP roots
            a_num = [
                float(sp.N(ai.subs({sp.Symbol(k): v for k, v in subs.items()})))
                for ai in parse_coeffs(args.coeffs)
            ]
            roots = np.roots(np.array(a_num, dtype=float))
            print("Verification: #RHP roots by numpy.roots =",
                  int(np.sum(np.real(roots) > args.tol)))

        # Optional 1-D scan even when subs are given
        if args.scan:
            name, lo, hi, step = _parse_scan1d_arg(args.scan)
            res1 = svc.scan1d(
                Scan1DRequest(
                    coeffs=args.coeffs,
                    symbol=name,
                    lo=lo, hi=hi, step=step,
                    use_lienard=args.lienard,
                )
            )
            print("\nSampled stability (t, stable):")
            for t, ok in res1.samples:
                print(f"  {t:.6g}, {ok}")
            if args.csv:
                path = iom.save_csv(Path(args.csv),
                                    ["t", "stable"],
                                    [[t, int(ok)] for t, ok in res1.samples])
                print(f"Saved CSV -> {path}")
        return 0

    # Purely numeric polynomial with no subs
    a = parse_coeffs(args.coeffs)
    if all(ai.is_number for ai in a):
        res = svc.numeric_check(
            NumericCheckRequest(
                coeffs=args.coeffs,
                subs={},
                use_lienard=args.lienard,
                tol=args.tol,
            )
        )
        print("Used:", res.used)
        print("a =", res.a_numeric)
        print("Δk values:")
        for i, d in enumerate(res.minors_numeric, 1):
            print(f"  Δ{i} = {d:.12g}")
        print("\nHurwitz stable?", res.ok)
        return 0

    # Symbolic region
    symres = svc.symbolic_region(
        SymbolicRegionRequest(
            coeffs=args.coeffs,
            symbols=args.symbols,
            solvefor=args.solvefor,
            use_lienard=args.lienard,
            intervals_pretty=args.intervals_pretty,
        )
    )
    print("Variables:", symres.variables)
    print("Used:", symres.used)
    print("Region:", symres.region)
    if symres.pretty:
        print("\nPretty intervals:\n  ", symres.pretty)
        print("LaTeX intervals:\n  ", symres.latex)

    # 1-D scan (only meaningful if exactly one variable)
    if args.scan and len(symres.variables) == 1:
        name, lo, hi, step = _parse_scan1d_arg(args.scan)
        res1 = svc.scan1d(
            Scan1DRequest(
                coeffs=args.coeffs,
                symbol=name,
                lo=lo, hi=hi, step=step,
                use_lienard=args.lienard,
            )
        )
        print("\nSampled stability (t, stable):")
        for t, ok in res1.samples:
            print(f"  {t:.6g}, {ok}")
        if args.csv:
            path = iom.save_csv(Path(args.csv),
                                ["t", "stable"],
                                [[t, int(ok)] for t, ok in res1.samples])
            print(f"Saved CSV -> {path}")

    # 2-D scan
    if args.scan2 and len(symres.variables) >= 2:
        (sx, xlo, xhi, dx), (sy, ylo, yhi, dy) = _parse_scan2d_arg(args.scan2)
        res2 = svc.scan2d(
            Scan2DRequest(
                coeffs=args.coeffs,
                sx=sx, sy=sy,
                xlo=xlo, xhi=xhi, dx=dx,
                ylo=ylo, yhi=yhi, dy=dy,
                use_lienard=args.lienard,
            )
        )
        print("\n2-D scan (ASCII heatmap: '█'=stable, '·'=unstable)")
        print(
            f"x={sx} in [{res2.xs.min():.6g},{res2.xs.max():.6g}] step {dx},  "
            f"y={sy} in [{res2.ys.min():.6g},{res2.ys.max():.6g}] step {dy}"
        )
        print(ascii_heatmap(res2.xs, res2.ys, res2.Z, invert_y=True))

        if args.csv2:
            X, Y = np.meshgrid(res2.xs, res2.ys)
            rows = [
                [float(X.ravel()[i]), float(Y.ravel()[i]), int(res2.Z.astype(int).ravel()[i])]
                for i in range(X.size)
            ]
            path = iom.save_csv(Path(args.csv2), ["x", "y", "stable"], rows)
            print(f"Saved CSV -> {path}")

        if args.png:
            msg = iom.save_png_heatmap(Path(args.png), res2.xs, res2.ys, res2.Z)
            if msg:
                print(msg)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
