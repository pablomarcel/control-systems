# -*- coding: utf-8 -*-
"""
CLI entry point for controllerTool.

Works in two modes:
  1) From project root (preferred):  python -m state_space_design.controllerTool.cli --help
  2) From inside this folder:        python cli.py --help
     (we install a small import shim when __package__ is not set)
"""
from __future__ import annotations

# --- Import shim so `python cli.py` works with relative imports ---
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    import os, sys
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from state_space_design.controllerTool.apis import run, RunRequest
    from state_space_design.controllerTool.io import PlotConfig, PlotService
else:
    # Normal package execution
    from .apis import run, RunRequest
    from .io import PlotConfig, PlotService

import argparse, logging, sys

def _normalize_negative_list_args(argv: list[str]) -> list[str] | None:
    """
    Make CLI robust to values that *start with '-'* by converting:
        --K_poles <value>   ->  --K_poles=<value>
        --obs_poles <value> ->  --obs_poles=<value>
    when the next token begins with '-' (argparse would otherwise treat it as a new option).
    """
    if argv is None:
        return None
    out = []
    i = 0
    sensitive = {"--K_poles", "--obs_poles"}
    while i < len(argv):
        tok = argv[i]
        if tok in sensitive and i + 1 < len(argv):
            nxt = argv[i + 1]
            if nxt.startswith("-") and not nxt.startswith("--="):
                out.append(f"{tok}={nxt}")
                i += 2
                continue
        out.append(tok)
        i += 1
    return out

def main(argv=None):
    argv = _normalize_negative_list_args(list(argv) if argv is not None else sys.argv[1:])
    ap = argparse.ArgumentParser(
        prog="state_space_design.controllerTool",
        description="Ogata Sec. 10-7 controllers with observers (SISO) — object-oriented tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, allow_abbrev=False)

    ap.add_argument("--num", required=True, help='Plant numerator, e.g. "1" or "10 20"')
    ap.add_argument("--den", required=True, help='Plant denominator, e.g. "1 0 1 0" or "1 10 24 0"')
    ap.add_argument("--K_poles", default=None, help='Controller poles, e.g. "-1+1j,-1-1j,-8" (tip: equals-form works best)')
    ap.add_argument("--obs_poles", default=None, help='Observer poles, e.g. "-4,-4" (tip: equals-form works best)')

    ap.add_argument("--ts", type=float, default=None, help="Settling-time target (sec) for auto K/observer")
    ap.add_argument("--undershoot", default=None, help='"low,high" undershoot for auto K (e.g. "0.25,0.35")')
    ap.add_argument("--obs_speed_factor", type=float, default=5.0, help="Observer speed vs controller sigma (auto)")

    ap.add_argument("--cfg", choices=["cfg1", "cfg2", "both"], default="both")
    ap.add_argument("--plots", choices=["none", "mpl", "plotly", "both"], default="both")
    ap.add_argument("--save_prefix", default=None)
    ap.add_argument("--ply_width", type=int, default=0)
    ap.add_argument("--verbose", action="store_true")

    args = ap.parse_args(argv)
    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
                        format="INFO: %(message)s")

    und = None
    if args.undershoot:
        parts = [float(x) for x in args.undershoot.replace(",", " ").split()]
        if len(parts) != 2:
            ap.error("--undershoot must be two numbers: low,high")
        und = (parts[0], parts[1])

    rr = RunRequest(
        num=args.num, den=args.den, K_poles=args.K_poles, obs_poles=args.obs_poles,
        cfg=args.cfg, ts=args.ts, undershoot=und, obs_speed_factor=args.obs_speed_factor
    )
    resp = run(rr)

    print("\n== Build Summary ==")
    print("K:", resp.result.K)
    print("Ke:\n", resp.result.Ke)
    numGc = resp.result.Gc.num[0][0]; denGc = resp.result.Gc.den[0][0]
    print("Gc num:", numGc); print("Gc den:", denGc)

    if args.plots != "none":
        systems = []
        if resp.result.T1 is not None: systems.append(("Config 1", resp.result.T1))
        if resp.result.T2 is not None: systems.append(("Config 2", resp.result.T2))
        PlotService(PlotConfig(plots=args.plots, save_prefix=args.save_prefix, ply_width=args.ply_width)).plot_closed_loop_bode_and_step(systems)

if __name__ == "__main__":
    main()
