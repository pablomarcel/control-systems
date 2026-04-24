#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, math, os, sys

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from pid_controllers.rootLocusTool.app import RootLocusApp
else:
    from .app import RootLocusApp

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Root-locus (with ζ-rays) and design-point visualization")
    ap.add_argument("--example", choices=["ogata_8_1"], help="Preset plant")
    ap.add_argument("--num", help="Numerator coefficients (CSV/space)")
    ap.add_argument("--den", help="Denominator coefficients (CSV/space)")
    # design scan
    ap.add_argument("--zeta_values", nargs='+', type=float, help="Explicit ζ list (0<ζ<1)")
    ap.add_argument("--zeta_range", nargs=2, type=float, metavar=('ZMIN','ZMAX'),
                    help="Scan ζ range (0<ZMIN<ZMAX<1)")
    ap.add_argument("--zeta_n", type=int, default=4, help="Number of ζ samples in range")
    ap.add_argument("--omega", nargs=3, type=float, metavar=('WMIN','WMAX','WN'),
                    default=[0.2, 12.0, 300], help="ω grid: min max N for the angle-scan")
    ap.add_argument("--kmin", type=int, default=-1); ap.add_argument("--kmax", type=int, default=1)
    ap.add_argument("--a", dest="a_override", type=float, help="Override zero location a for plotting (zeros at s=-a)")
    # rays clipping + axes
    ap.add_argument("--ray_wmin", type=float, default=0.0, help="Lower ω bound for ζ-rays on the plot")
    ap.add_argument("--ray_scale", type=float, default=1.05, help="If no --ylim, use ray_scale*max|Im(locus)|")
    ap.add_argument("--xlim", nargs=2, type=float, help="x-axis limits: xmin xmax")
    ap.add_argument("--ylim", nargs=2, type=float, help="y-axis limits: ymin ymax")
    # plotting / IO
    ap.add_argument("--backend", choices=["mpl","plotly"], default="plotly")
    ap.add_argument("--save", help="Save plot (PNG for MPL, HTML for Plotly) in ./out/ when relative")
    ap.add_argument("--title", default="Root Locus with ζ-rays")
    ap.add_argument("--no_plot", action="store_true")
    # exports + analysis
    ap.add_argument("--export_json", help="Export summary JSON in ./out/ when relative")
    ap.add_argument("--export_csv", help="Export detailed rows CSV in ./out/ when relative")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--settle", type=float, default=0.02)
    ap.add_argument("--precision", type=int, default=6)
    return ap

def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    app = RootLocusApp()
    if getattr(args, "no_plot", False):
        args.save = None  # just compute/export
    result = app.run(
        example=args.example, num=args.num, den=args.den, backend=args.backend, save=args.save,
        export_json=args.export_json, export_csv=args.export_csv,
        zeta_values=args.zeta_values, zeta_range=args.zeta_range, zeta_n=args.zeta_n,
        omega=tuple([args.omega[0], args.omega[1], int(args.omega[2])]),
        kmin=args.kmin, kmax=args.kmax, a_override=args.a_override,
        ray_wmin=args.ray_wmin, ray_scale=args.ray_scale, xlim=tuple(args.xlim) if args.xlim else None,
        ylim=tuple(args.ylim) if args.ylim else None, title=args.title,
        analyze=args.analyze, settle=args.settle, precision=args.precision
    )
    # compact stdout report
    fmt = lambda x,p=6: (f"{x:.{p}g}" if isinstance(x,(int,float)) and hasattr(x,'__float__') else str(x))
    print("=== Root-Locus (OOP) ===")
    print(f"a_plot={fmt(result['a_plot'])}; limits x={result['xlim']} y={result['ylim']}")
    if result.get("s_row"):
        s = result["s_row"]
        print(f"s*: ζ={fmt(s['zeta'])}, ω={fmt(s['omega'])}, a={fmt(s['a'])}, Kp={fmt(s['Kp'])}, Ti={fmt(s['Ti'])}, Td={fmt(s['Td'])}")
    if result.get("json_path"): print(f"Saved JSON → {result['json_path']}")
    if result.get("csv_path"):  print(f"Saved CSV  → {result['csv_path']}")

if __name__ == "__main__":
    main()
