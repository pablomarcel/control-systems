
# SPDX-License-Identifier: MIT
from __future__ import annotations
import argparse, sys, os
from pathlib import Path

# --------------------------------------------------------------
# Import shim so `python cli.py` (run inside the folder) works
# --------------------------------------------------------------
if __package__ in (None, ""):
    # Running as a script from inside statePlotsTool/
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from stateSpaceDesign.statePlotsTool.app import StatePlotsApp, main_kwargs_from_args
    from stateSpaceDesign.statePlotsTool.apis import StatePlotsAPI
    RUN_LOCAL = True
    BASE_DIR = os.path.dirname(__file__)
    IN_DIR = os.path.join(BASE_DIR, "in")
    OUT_DIR = os.path.join(BASE_DIR, "out")
else:
    # Normal module execution: python -m stateSpaceDesign.statePlotsTool.cli
    from .app import StatePlotsApp, main_kwargs_from_args
    from .apis import StatePlotsAPI
    RUN_LOCAL = False
    BASE_DIR = os.path.dirname(__file__)
    IN_DIR = os.path.join(BASE_DIR, "in")
    OUT_DIR = os.path.join(BASE_DIR, "out")

def _normalize_data_path(data: str) -> str:
    """If running locally and `data` is relative with no dir, look in ./in/."""
    if os.path.isabs(data):
        return data
    if RUN_LOCAL:
        cand = os.path.join(IN_DIR, data) if not os.path.dirname(data) else data
        return cand
    return data

def _ensure_out_path(name: str | None) -> str | None:
    """
    If a save name is provided without a directory, put it under ./out (local run).
    Otherwise, pass-through.
    """
    if not name:
        return None
    if os.path.dirname(name):
        # Directory was provided; ensure it exists
        os.makedirs(os.path.dirname(name), exist_ok=True)
        return name
    # No directory -> use local OUT_DIR
    os.makedirs(OUT_DIR, exist_ok=True)
    return os.path.join(OUT_DIR, name)

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog='statePlotsTool',
        description='State-space plots (IC and STEP) from controller/IO JSON',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument('--data', required=True, help='JSON filename (relative to ./in when running locally, or absolute)')
    ap.add_argument('--scenario', choices=['auto','ic','step'], default='auto', help='Detect or force scenario')
    ap.add_argument('--what', choices=['auto','y','states','both'], default='auto', help='What to plot (STEP only). IC always plots states.')
    ap.add_argument('--subplots', action='store_true', help='Ogata-style stacked subplots instead of overlays')
    ap.add_argument('--x0', default=None, help='IC vector "1 0 0" (IC scenario)')
    ap.add_argument('--t',  default='0:0.01:4', help='Time vector "t0:dt:tf" or explicit list')
    ap.add_argument('--backend', choices=['mpl','plotly','both','none'], default='both', help='Plotting backend(s)')
    ap.add_argument('--save_png',  default=None, help='PNG filename (defaults to ./out/ when running locally)')
    ap.add_argument('--save_html', default=None, help='Plotly HTML filename (defaults to ./out/ when running locally)')
    ap.add_argument('--save_csv',  default=None, help='CSV filename (defaults to ./out/ when running locally)')
    ap.add_argument('--no_show', action='store_true', help='Do not pop up GUI windows')
    return ap

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = build_parser()
    args = ap.parse_args(argv)

    # Normalize paths for local run
    args.data = _normalize_data_path(args.data)
    args.save_png  = _ensure_out_path(args.save_png)
    args.save_html = _ensure_out_path(args.save_html)
    args.save_csv  = _ensure_out_path(args.save_csv)

    app = StatePlotsApp(api=StatePlotsAPI())
    kw = main_kwargs_from_args(args)
    # main_kwargs_from_args resolves relative data path using package defaults when not absolute.
    # Since we already normalized above for local run, pass through.
    res = app.run(**kw)

    # minimal console output
    print('Scenario:', res['scenario'])
    if res.get('paths'):
        for k,v in res['paths'].items():
            if v:
                print(f'Wrote {k}:', v)

if __name__ == '__main__':
    main()
