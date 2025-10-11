#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import logging
import os
import sys

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Running as a script from within the package folder.
    # Add project root to sys.path (../../)
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    # Import absolute modules
    from frequencyResponse.bodeTool.apis import BodeConfig
    from frequencyResponse.bodeTool.app import BodeApp
else:
    # Normal package execution (e.g., `python -m frequencyResponse.bodeTool.cli`)
    from .apis import BodeConfig
    from .app import BodeApp


def _level(v: int):
    return logging.DEBUG if v>=2 else (logging.INFO if v==1 else logging.INFO)


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Bode/Nyquist/Nichols with margins, bandwidth, resonant peak.")
    # G(s) inputs
    ap.add_argument("--num"); ap.add_argument("--den")
    ap.add_argument("--gain", type=float); ap.add_argument("--zeros"); ap.add_argument("--poles")
    ap.add_argument("--fnum"); ap.add_argument("--fden"); ap.add_argument("--K", type=float, default=1.0)
    # H(s)
    ap.add_argument("--hnum"); ap.add_argument("--hden")
    ap.add_argument("--hgain", type=float); ap.add_argument("--hzeros"); ap.add_argument("--hpoles")
    ap.add_argument("--hfnum"); ap.add_argument("--hfden"); ap.add_argument("--hK", type=float, default=1.0)
    # frequency grid
    ap.add_argument("--wmin", type=float); ap.add_argument("--wmax", type=float); ap.add_argument("--npts", type=int, default=2000)
    # plots/exports
    ap.add_argument("--bode", action="store_true"); ap.add_argument("--nyquist", action="store_true"); ap.add_argument("--nichols", action="store_true")
    ap.add_argument("--step", action="store_true"); ap.add_argument("--plotly", action="store_true")
    ap.add_argument("--save-png"); ap.add_argument("--save-html"); ap.add_argument("--save-json")
    ap.add_argument("--title", default="Bode of L(s)")
    ap.add_argument("-v","--verbose", action="count", default=0)
    return ap


def main(argv=None):
    ap = build_arg_parser()
    args = ap.parse_args(argv)
    cfg = BodeConfig(
        num=args.num, den=args.den, gain=args.gain, zeros=args.zeros, poles=args.poles,
        fnum=args.fnum, fden=args.fden, K=args.K,
        hnum=args.hnum, hden=args.hden, hgain=args.hgain, hzeros=args.hzeros, hpoles=args.hpoles,
        hfnum=args.hfnum, hfden=args.hfden, hK=args.hK,
        wmin=args.wmin, wmax=args.wmax, npts=args.npts,
        bode=args.bode, nyquist=args.nyquist, nichols=args.nichols, step=args.step, plotly=args.plotly,
        save_png=args.save_png, save_html=args.save_html, save_json=args.save_json,
        title=args.title, verbose=args.verbose
    )
    app = BodeApp(level=_level(cfg.verbose))
    result = app.run(cfg)
    print("\n== Frequency-Response Summary ==")
    print(f"L(s) = {result.pretty_tf}")
    print(f"Gain margin      : {result.margins.gm:.6g}  ({result.margins.gm_db:.3g} dB) at w_pc = {result.margins.wpc:.6g} rad/s")
    print(f"Phase margin     : {result.margins.pm:.6g} deg at w_gc = {result.margins.wgc:.6g} rad/s")
    print(f"Closed-loop Mr   : {result.closedloop.Mr_db:.3g} dB at w_r = {result.closedloop.wr:.6g} rad/s")
    print(f"Closed-loop w_bw : {result.closedloop.wb:.6g} rad/s")
    print("Hints:"); [print(" •", h) for h in result.hints]
    app.render(cfg, result)


if __name__ == "__main__":
    main()
