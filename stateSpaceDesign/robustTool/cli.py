from __future__ import annotations
import argparse, logging as log, os
from .apis import RunRequest
from .app import RobustApp
from .io import save_json

def build_parser():
    p = argparse.ArgumentParser(prog="stateSpaceDesign.robustTool", description="Robust control sweeps (Ogata §10-9).")
    # plant
    p.add_argument("--num", required=True, help="Plant numerator coeffs: e.g. '10 20'")
    p.add_argument("--den", required=True, help="Plant denominator coeffs: e.g. '1 10 24 0'")
    # controller
    p.add_argument("--pid", default=None, help="kp,ki,kd[,nd]")
    p.add_argument("--K_num", default=None); p.add_argument("--K_den", default=None)
    # weights
    p.add_argument("--Wm_num", default=None); p.add_argument("--Wm_den", default=None)
    p.add_argument("--Ws_num", default=None); p.add_argument("--Ws_den", default=None)
    p.add_argument("--Wa_num", default=None); p.add_argument("--Wa_den", default=None)
    # sweep/grid
    p.add_argument("--wmin", type=float, default=1e-2)
    p.add_argument("--wmax", type=float, default=1e2)
    p.add_argument("--npts", type=int, default=400)
    # step
    p.add_argument("--step", action="store_true")
    p.add_argument("--tfinal", type=float, default=8.0)
    p.add_argument("--dt", type=float, default=0.01)
    # plots
    p.add_argument("--plots", choices=["mpl","plotly","both","none"], default="mpl")
    # io
    p.add_argument("--export-json", default=None, help="Save results JSON to stateSpaceDesign/robustTool/out/<name>.json")
    p.add_argument("--loglevel", choices=["DEBUG","INFO","WARNING","ERROR"], default="INFO")
    return p

def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    log.basicConfig(level=getattr(log, args.loglevel), format="%(levelname)s: %(message)s")

    req = RunRequest(**vars(args))
    app = RobustApp()
    res = app.run(req)

    if args.export_json:
        out = save_json(res.to_jsonable(), args.export_json)
        print(f"Saved JSON → {out}")

if __name__ == "__main__":
    main()
