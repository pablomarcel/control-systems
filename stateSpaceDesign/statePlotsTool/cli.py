# SPDX-License-Identifier: MIT
from __future__ import annotations
import argparse, sys
from .app import StatePlotsApp, main_kwargs_from_args
from .apis import StatePlotsAPI

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog='statePlotsTool',
        description='State-space plots (IC and STEP) from controller/IO JSON',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument('--data', required=True, help='JSON filename (relative to package in/ or absolute)')
    ap.add_argument('--scenario', choices=['auto','ic','step'], default='auto', help='Detect or force scenario')
    ap.add_argument('--what', choices=['auto','y','states','both'], default='auto', help='What to plot (STEP only). IC always plots states.')
    ap.add_argument('--subplots', action='store_true', help='Ogata-style stacked subplots instead of overlays')
    ap.add_argument('--x0', default=None, help='IC vector "1 0 0" (IC scenario)')
    ap.add_argument('--t',  default='0:0.01:4', help='Time vector "t0:dt:tf" or explicit list')
    ap.add_argument('--backend', choices=['mpl','plotly','both','none'], default='both', help='Plotting backend(s)')
    ap.add_argument('--save_png',  default=None, help='PNG filename (saved under package out/)')
    ap.add_argument('--save_html', default=None, help='Plotly HTML filename (saved under package out/)')
    ap.add_argument('--save_csv',  default=None, help='CSV filename (saved under package out/)')
    ap.add_argument('--no_show', action='store_true', help='Do not pop up GUI windows')
    return ap

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = build_parser()
    args = ap.parse_args(argv)
    app = StatePlotsApp(api=StatePlotsAPI())
    kw = main_kwargs_from_args(args)
    res = app.run(**kw)
    # minimal console output
    print('Scenario:', res['scenario'])
    if res.get('paths'):
        for k,v in res['paths'].items():
            if v:
                print(f'Wrote {k}:', v)

if __name__ == '__main__':
    main()
