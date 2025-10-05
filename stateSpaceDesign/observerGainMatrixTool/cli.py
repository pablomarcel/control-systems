from __future__ import annotations
import argparse, json, logging, sys
import numpy as np
from .apis import ObserverRequest
from .app import ObserverGainMatrixApp
from .utils import CSV_CPLX_RE

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Observer Gain Matrix Tool — stateSpaceDesign.observerGainMatrixTool")
    ap.add_argument("--A", required=True, help='e.g. "0 1; 20.6 0"')
    ap.add_argument("--B", default=None, help='e.g. "0; 1" (required for K / closed-loop / TF / sim)')
    ap.add_argument("--C", required=True, help='e.g. "1 0" or "1 0; 0 1"')
    ap.add_argument("--poles", nargs="+", type=complex, required=True,
                    help="Observer poles (n values). Example: -8 -8, or -10 -12, or -1.8+2.4j -1.8-2.4j")
    ap.add_argument("--method", choices=["auto","place","ack"], default="auto")
    ap.add_argument("--place_fallback", choices=["none","ack","jitter"], default="none")
    ap.add_argument("--jitter_eps", type=float, default=1e-6)

    ap.add_argument("--K", type=str, default=None, help='Explicit K row, e.g. "29.6 3.6"')
    ap.add_argument("--K_poles", nargs="?", default=None,
                    help='Controller poles as a single quoted CSV string, e.g. "-1.8+2.4j,-1.8-2.4j"')
    ap.add_argument("--K_poles_list", nargs="+", default=None,
                    help='Controller poles as separate tokens, e.g. "-1.8+2.4j" "-1.8-2.4j"')

    ap.add_argument("--compute_closed_loop", action="store_true")
    ap.add_argument("--x0", type=str, default=None)
    ap.add_argument("--e0", type=str, default=None)
    ap.add_argument("--t_final", type=float, default=0.0)
    ap.add_argument("--dt", type=float, default=0.01)

    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--equations", action="store_true", help="(reserved for future pretty expansions)")
    ap.add_argument("--eq_style", choices=["auto","ascii","numpy","both"], default="auto")
    ap.add_argument("--latex", default=None, help="Write LaTeX snippet to this filename under out/")
    ap.add_argument("--export_json", default=None, help="Write JSON to this filename under out/")
    ap.add_argument("--log", default="WARNING", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return ap

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    ap = build_parser()
    # parse allowing unknown (to capture stray CSV after --K_poles that begins with '-')
    args, unknown = ap.parse_known_args(argv)
    logging.basicConfig(level=getattr(logging, str(args.log).upper(), logging.WARNING),
                        format="%(levelname)s: %(message)s")
    # If --K_poles missing but a CSV-looking token is present in unknowns, capture it
    if args.K_poles is None and not args.K and not args.K_poles_list:
        for tok in unknown:
            if CSV_CPLX_RE.match(tok):
                args.K_poles = tok
                break

    req = ObserverRequest(
        A=args.A, C=args.C, poles=args.poles, method=args.method,
        place_fallback=args.place_fallback, jitter_eps=args.jitter_eps,
        B=args.B, K=args.K, K_poles_csv=args.K_poles, K_poles_list=args.K_poles_list,
        compute_closed_loop=args.compute_closed_loop, x0=args.x0, e0=args.e0,
        t_final=args.t_final, dt=args.dt, pretty=args.pretty, equations=args.equations,
        eq_style=args.eq_style, latex_out=(args.latex if args.latex else None)
    )
    app = ObserverGainMatrixApp()
    try:
        resp = app.run(req)
    except Exception as e:
        logging.error(str(e))
        return 2

    if args.export_json:
        from .io import OutputManager
        OutputManager().write_json(resp.data, args.export_json)

    # Pretty or JSON to stdout
    if args.pretty and resp.pretty_blocks:
        print("\n".join(resp.pretty_blocks))
    else:
        print(json.dumps(resp.data, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
