
from __future__ import annotations
import argparse
from .app import ZeroPoleApp, AppConfig

def build_parser():
    p = argparse.ArgumentParser(description="Two-DOF zero-placement (Ogata §8-7) — zeroPoleTool")
    p.add_argument("--arch", choices=["fig8-31","fig8-30"], default="fig8-31")

    g = p.add_argument_group("Plant")
    g.add_argument("--plant-form", choices=["coeff","poly","zpk"], required=True)
    g.add_argument("--num", type=str); g.add_argument("--den", type=str)
    g.add_argument("--num-poly", type=str); g.add_argument("--den-poly", type=str)
    g.add_argument("--gain", type=float); g.add_argument("--zeros", type=str); g.add_argument("--poles", type=str)

    grd = p.add_argument_group("Pole grid (a,b,c)")
    grd.add_argument("--a-vals", type=str); grd.add_argument("--b-vals", type=str); grd.add_argument("--c-vals", type=str)
    grd.add_argument("--a-range", type=float, nargs=2); grd.add_argument("--a-n", type=int)
    grd.add_argument("--b-range", type=float, nargs=2); grd.add_argument("--b-n", type=int)
    grd.add_argument("--c-range", type=float, nargs=2); grd.add_argument("--c-n", type=int)

    r = p.add_argument_group("Requirements (reference step)")
    r.add_argument("--os-min", type=float, default=0.0)
    r.add_argument("--os-max", type=float, default=100.0)
    r.add_argument("--ts-max", type=float, default=10.0)
    r.add_argument("--settle-tol", type=float, default=0.02)

    rank = p.add_argument_group("Ranking")
    rank.add_argument("--rank-dist-peak-weight", type=float, default=0.0)

    o = p.add_argument_group("Outputs")
    o.add_argument("--save-prefix", type=str, default="zp_design")
    o.add_argument("--plot-prefix", type=str, default="zp_design")
    o.add_argument("--export-json", action="store_true")
    o.add_argument("--export-csv", action="store_true")
    o.add_argument("--plots", nargs="*", default=["step_ref"], choices=["step_ref","step_dist","ramp_ref","accel_ref"])

    b = p.add_argument_group("Behavior")
    b.add_argument("--best-effort", action="store_true")
    b.add_argument("--debug", action="store_true")
    b.add_argument("--no-progress", action="store_true")
    return p

def main():
    args = build_parser().parse_args()
    cfg = AppConfig(
        # Plant
        plant_form=args.plant_form,
        num=getattr(args, "num", None), den=getattr(args, "den", None),
        num_poly=getattr(args, "num_poly", None), den_poly=getattr(args, "den_poly", None),
        gain=getattr(args, "gain", None), zeros=getattr(args, "zeros", None), poles=getattr(args, "poles", None),
        # Arch & grids
        arch=args.arch,
        a_vals=args.a_vals, b_vals=args.b_vals, c_vals=args.c_vals,
        a_range=args.a_range, a_n=args.a_n, b_range=args.b_range, b_n=args.b_n,
        c_range=args.c_range, c_n=args.c_n,
        # Specs & behavior
        os_min=args.os_min, os_max=args.os_max, ts_max=args.ts_max, settle_tol=args.settle_tol,
        rank_dist_peak_weight=args.rank_dist_peak_weight,
        best_effort=args.best_effort, export_json=args.export_json, export_csv=args.export_csv,
        plots=args.plots, no_progress=args.no_progress, debug=args.debug,
        save_prefix=args.save_prefix, plot_prefix=args.plot_prefix,
    )
    ZeroPoleApp(cfg).run()

if __name__ == "__main__":
    main()
