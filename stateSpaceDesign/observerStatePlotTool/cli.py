from __future__ import annotations
import argparse
from .apis import PlotRequest, SimulateOptions
from .app import ObserverStatePlotApp

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="observerStatePlotTool",
        description="Observer/Controller state plotter (OOP refactor).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument("--data", required=True, help="observer_gain_matrix.py JSON (with simulation or A_augmented)")
    ap.add_argument("--what", default="auto", help='Comma list from {x,e,err,y,u} or "auto"')
    ap.add_argument("--subplots", action="store_true", help="Stack series as Ogata-style subplots")
    ap.add_argument("--backend", choices=["mpl","plotly","both","none"], default="both", help="Plotting backend(s)")
    ap.add_argument("--save_png",  default=None, help="PNG filename (defaults to pkg out/)")
    ap.add_argument("--save_html", default=None, help="Plotly HTML filename (defaults to pkg out/)")
    ap.add_argument("--save_csv",  default=None, help="CSV filename (defaults to pkg out/)")
    ap.add_argument("--no_show", action="store_true", help="Do not show MPL figures")
    ap.add_argument("--simulate_if_missing", action="store_true",
                    help="If 'simulation' missing, simulate A_augmented with x0,e0,t.")
    ap.add_argument("--t", default="0:0.01:4", help='Time vector "t0:dt:tf" (used if we simulate)')
    ap.add_argument("--x0", default=None, help='x(0) as "1 0 ..."  (used if we simulate)')
    ap.add_argument("--e0", default=None, help='e(0) as "0.5 0 ..." (used if we simulate)')
    return ap

def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)

    req = PlotRequest(
        data_path=args.data,
        what=args.what,
        backend=args.backend,
        subplots=args.subplots,
        save_png=args.save_png,
        save_html=args.save_html,
        save_csv=args.save_csv,
        no_show=args.no_show,
        simulate=SimulateOptions(
            enabled=args.simulate_if_missing,
            t=args.t,
            x0=args.x0,
            e0=args.e0,
        )
    )

    # Allow 'none' backend for CSV-only exports
    if req.backend == "none":
        req.backend = "mpl"  # internally use mpl but don't show and don't save plot unless asked
        req.no_show = True
        req.save_png = None
        req.save_html = None

    app = ObserverStatePlotApp()
    resp = app.run(req)
    if resp.csv_path:
        print(f"[OK] Wrote CSV: {resp.csv_path}")
    if resp.png_path:
        print(f"[OK] Wrote PNG: {resp.png_path}")
    if resp.html_path:
        print(f"[OK] Wrote HTML: {resp.html_path}")

if __name__ == "__main__":
    main()
