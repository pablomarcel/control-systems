from __future__ import annotations
import argparse, os, warnings
from .app import PlotToolApp
from .apis import PlotService, PlotRequest
from .utils import build_logger, parse_csv_vals, parse_range4

def build_parser():
    ap = argparse.ArgumentParser(
        description="Frequency-response plotTool (Bode, Nyquist, Nichols) — modernControl"
    )
    # scalar TF
    ap.add_argument("--num"); ap.add_argument("--den")
    ap.add_argument("--gain", type=float); ap.add_argument("--zeros"); ap.add_argument("--poles")
    ap.add_argument("--fnum"); ap.add_argument("--fden"); ap.add_argument("--K", type=float, default=1.0)
    # state-space
    ap.add_argument("--A"); ap.add_argument("--B"); ap.add_argument("--C"); ap.add_argument("--D")
    # scale
    ap.add_argument("--scale", type=float)
    # frequency grid
    ap.add_argument("--wmin", type=float); ap.add_argument("--wmax", type=float); ap.add_argument("--npts", type=int, default=400)
    # plots
    ap.add_argument("--bode", action="store_true"); ap.add_argument("--nyquist", action="store_true")
    ap.add_argument("--nichols", action="store_true"); ap.add_argument("--nichols-grid", action="store_true")
    ap.add_argument("--nichols-closedloop", action="store_true")
    ap.add_argument("--nyq-markers", action="store_true"); ap.add_argument("--nyq-samples", type=int, default=0)
    ap.add_argument("--plotly", action="store_true")
    # ranges & markers
    ap.add_argument("--wmarks"); ap.add_argument("--nichols-range")
    # Nichols grid customization
    ap.add_argument("--nichols-Mdb", nargs="*", type=float)
    ap.add_argument("--nichols-Mdb-csv", type=str)
    ap.add_argument("--nichols-Ndeg", nargs="*", type=float)
    ap.add_argument("--nichols-Ndeg-csv", type=str)
    ap.add_argument("--nichols-no-grid-labels", action="store_true")
    # outputs
    ap.add_argument("--save-png", help="Folder for PNG files (Matplotlib).")
    ap.add_argument("--save-html", help="Base name for Plotly HTML (suffixes added).")
    ap.add_argument("--save-json", help="Write a JSON report.")
    ap.add_argument("--title", default="Frequency Response")
    ap.add_argument("-v", "--verbose", action="count", default=0)
    return ap

import os, sys, platform, traceback

def _debug_banner(args):
    try:
        import numpy, control, matplotlib, plotly
    except Exception as e:
        numpy = control = matplotlib = plotly = None
    print("\n[plotTool DEBUG] Python:", sys.version)
    print("[plotTool DEBUG] Platform:", platform.platform())
    print("[plotTool DEBUG] CWD:", os.getcwd())
    print("[plotTool DEBUG] argv:", sys.argv)
    print("[plotTool DEBUG] parsed args:", args)
    if numpy:
        print("[plotTool DEBUG] numpy:", numpy.__version__)
    if control:
        print("[plotTool DEBUG] python-control:", getattr(control, '__version__', '?'))
    if matplotlib:
        print("[plotTool DEBUG] matplotlib:", matplotlib.__version__)
        try:
            import matplotlib
            print("[plotTool DEBUG] MPL backend:", matplotlib.get_backend())
        except Exception:
            pass
    if plotly:
        print("[plotTool DEBUG] plotly:", plotly.__version__)


def main(argv=None):
    argv = argv or None
    ap = build_parser()
    args = ap.parse_args(argv)

    debug = bool(os.environ.get("PLOTTOOL_DEBUG", ""))
    if debug:
        _debug_banner(args)

    log = build_logger("plotTool", level=(10 if args.verbose and args.verbose>=1 else 20))

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
        wmarks = ([float(x) for x in args.wmarks.replace(";", ",").split(",") if x.strip()] if args.wmarks else None),
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
    except Exception as exc:
        if debug:
            print("[plotTool DEBUG] Exception raised:")
            traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
