#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""frequency_response.plotTool.cli
Import shim so you can run both:
  - python -m frequency_response.plotTool.cli
  - python cli.py (from inside frequency_response/plotTool)
"""
import argparse
import os
import sys
import warnings
import platform
import traceback

# Import shim
if __package__ in (None, ""):
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from frequency_response.plotTool.app import PlotToolApp  # type: ignore
    from frequency_response.plotTool.apis import PlotService, PlotRequest  # type: ignore
    from frequency_response.plotTool.utils import build_logger, parse_csv_vals, parse_range4  # type: ignore
else:
    from .app import PlotToolApp
    from .apis import PlotService, PlotRequest
    from .utils import build_logger, parse_csv_vals, parse_range4

def build_parser():
    ap = argparse.ArgumentParser(description="Frequency-response plotTool (Bode, Nyquist, Nichols) — modernControl")
    ap.add_argument("--num"); ap.add_argument("--den")
    ap.add_argument("--gain", type=float); ap.add_argument("--zeros"); ap.add_argument("--poles")
    ap.add_argument("--fnum"); ap.add_argument("--fden"); ap.add_argument("--K", type=float, default=1.0)
    ap.add_argument("--A"); ap.add_argument("--B"); ap.add_argument("--C"); ap.add_argument("--D")
    ap.add_argument("--scale", type=float)
    ap.add_argument("--wmin", type=float); ap.add_argument("--wmax", type=float); ap.add_argument("--npts", type=int, default=400)
    ap.add_argument("--bode", action="store_true"); ap.add_argument("--nyquist", action="store_true")
    ap.add_argument("--nichols", action="store_true"); ap.add_argument("--nichols-grid", action="store_true")
    ap.add_argument("--nichols-closedloop", action="store_true")
    ap.add_argument("--nyq-markers", action="store_true"); ap.add_argument("--nyq-samples", type=int, default=0)
    ap.add_argument("--plotly", action="store_true")
    ap.add_argument("--wmarks"); ap.add_argument("--nichols-range")
    ap.add_argument("--nichols-Mdb", nargs="*", type=float)
    ap.add_argument("--nichols-Mdb-csv", type=str)
    ap.add_argument("--nichols-Ndeg", nargs="*", type=float)
    ap.add_argument("--nichols-Ndeg-csv", type=str)
    ap.add_argument("--nichols-no-grid-labels", action="store_true")
    ap.add_argument("--save-png", help="Folder for PNG files (Matplotlib)." )
    ap.add_argument("--save-html", help="Base name for Plotly HTML (suffixes added)." )
    ap.add_argument("--save-json", help="Write a JSON report." )
    ap.add_argument("--title", default="Frequency Response")
    ap.add_argument("-v", "--verbose", action="count", default=0)
    return ap

def _debug_banner(args):
    try:
        import numpy, control, matplotlib, plotly
    except Exception:
        numpy = control = matplotlib = plotly = None
    print("\n[plotTool DEBUG] Python:", sys.version)
    print("[plotTool DEBUG] Platform:", platform.platform())
    print("[plotTool DEBUG] CWD:", os.getcwd())
    print("[plotTool DEBUG] argv:", sys.argv)
    print("[plotTool DEBUG] parsed args:", args)
    if numpy:
        print("[plotTool DEBUG] numpy:", numpy.__version__)
    if control:
        print("[plotTool DEBUG] python-control:", getattr(control, "__version__", "?"))
    if matplotlib:
        try:
            import matplotlib as _mpl
            print("[plotTool DEBUG] matplotlib:", _mpl.__version__)
            print("[plotTool DEBUG] MPL backend:", _mpl.get_backend())
        except Exception:
            pass
    if plotly:
        print("[plotTool DEBUG] plotly:", plotly.__version__)

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = build_parser()
    args = ap.parse_args(argv)

    debug = bool(os.environ.get("PLOTTOOL_DEBUG", ""))
    if debug:
        _debug_banner(args)

    _ = build_logger("plotTool", level=(10 if args.verbose and args.verbose >= 1 else 20))

    req = PlotRequest(
        bode = args.bode,
        nyquist = args.nyquist,
        nichols = args.nichols,
        nichols_grid = args.nichols_grid,
        nichols_closedloop = args.nichols_closedloop,
        plotly = args.plotly,
        nyq_markers = args.nyq_markers,
        nyq_samples = args.nyq_samples,
        wmin = args.wmin, wmax = args.wmax, npts = args.npts,
        wmarks = ([float(x) for x in (args.wmarks or "").replace(";", ",").split(",") if x.strip()] if args.wmarks else None),
        nichols_range = parse_range4(args.nichols_range),
        nichols_Mdb = (args.nichols_Mdb if (args.nichols_Mdb and len(args.nichols_Mdb)>0) else parse_csv_vals(args.nichols_Mdb_csv)),
        nichols_Ndeg = (args.nichols_Ndeg if (args.nichols_Ndeg and len(args.nichols_Ndeg)>0) else parse_csv_vals(args.nichols_Ndeg_csv)),
        nichols_no_grid_labels = args.nichols_no_grid_labels,
        save_png_dir = args.save_png,
        save_html_base = args.save_html,
        save_json_path = args.save_json,
        title = args.title
    )
    app = PlotToolApp()
    svc = PlotService(app)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            svc.run(args, req)
    except Exception:
        if debug:
            print("[plotTool DEBUG] Exception raised:")
            traceback.print_exc()
        raise

if __name__ == "__main__":
    raise SystemExit(main())
