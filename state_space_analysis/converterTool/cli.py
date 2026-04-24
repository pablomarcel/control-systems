from __future__ import annotations
import argparse
from .apis import RunRequest
from .app import ConverterApp

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Convert between TF and SS (Ogata §2-6).")
    p.add_argument("--num", type=str, help="TF numerator (descending powers), e.g. '1,0'")
    p.add_argument("--den", type=str, help="TF denominator (descending), e.g. '1,14,56,160'")
    p.add_argument("--A", type=str); p.add_argument("--B", type=str)
    p.add_argument("--C", type=str); p.add_argument("--D", type=str)
    p.add_argument("--iu", type=int, default=0, help="Input channel (0-based) for SS step plot")
    p.add_argument("--tfinal", type=float, default=8.0)
    p.add_argument("--dt", type=float, default=1e-3)
    p.add_argument("--no-plot", dest="no_plot", action="store_true", help="Skip plotting")
    p.add_argument("--sympy", action="store_true", help="SymPy pretty TF (SISO)")
    p.add_argument("--out-prefix", type=str, help="Prefix for files saved under out/ (without extension)")
    p.add_argument("--log", type=str, default="INFO", help="Log level: DEBUG, INFO, WARNING, ERROR")
    return p

def args_to_request(args: argparse.Namespace) -> RunRequest:
    return RunRequest(
        num=args.num, den=args.den, A=args.A, B=args.B, C=args.C, D=args.D,
        iu=args.iu, tfinal=args.tfinal, dt=args.dt, sympy=args.sympy,
        no_plot=args.no_plot, out_prefix=args.out_prefix, log=args.log
    )

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    app = ConverterApp()
    res = app.run(args_to_request(args))
    raise SystemExit(0 if res.ok else 1)

if __name__ == "__main__":
    main()
