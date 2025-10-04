
# cli.py — CLI entry point: python -m stateSpaceAnalysis.stateSolnTool.cli
from __future__ import annotations
import argparse
from .app import StateSolnApp

def main():
    p = argparse.ArgumentParser(
        description="Solve ẋ=Ax+Bu from a SISO transfer function: x(t)=Φ(t)x0+∫Φ(t-τ)Bu(τ)dτ."
    )
    g_in = p.add_argument_group("Input TF")
    g_in.add_argument("--tf", type=str, help='Rational string, e.g. "(s+3)/(s^2+3*s+2)".')
    g_in.add_argument("--num", type=str, help='Numerator as CSV "1,3" or poly "s+3".')
    g_in.add_argument("--den", type=str, help='Denominator as CSV "1,3,2" or poly "s^2+3*s+2".')
    g_in.add_argument("--example", type=str, choices=["ogata_9_1"], help="Use Example 9-1 TF.")

    g_opt = p.add_argument_group("Options")
    g_opt.add_argument("--canonical", default="controllable",
                       choices=["controllable","observable","diagonal","jordan"],
                       help="Which realization to use for (A,B). Default: controllable.")
    g_opt.add_argument("--u", type=str, default="1",
                       help='Input u(t) as a SymPy expr in t. Examples: "1", "exp(-t)", "sin(2*t)".')
    g_opt.add_argument("--x0", type=str, help='Initial state as CSV (length n). Default zeros.')
    g_opt.add_argument("--t0", type=float, default=0.0, help="Initial time t0 (default 0).")
    g_opt.add_argument("--eval", type=float, help="Evaluate x(t) at this time.")
    g_opt.add_argument("--numeric", action="store_true", help="Numeric print when --eval is given.")
    g_opt.add_argument("--digits", type=int, default=8, help="Digits for numeric print.")
    g_opt.add_argument("--pretty", action="store_true", help="Pretty Unicode matrices (symbolic).")
    g_opt.add_argument("--export-json", type=str, help="Write Φ, x_hom, x_part (and x) to JSON.")
    g_opt.add_argument("--verify", action="store_true", help="Verify ODE and initial condition.")
    g_opt.add_argument("--tol", type=float, default=1e-9, help="Tolerance for numeric fallback in --verify.")
    g_opt.add_argument("--log", type=str, default="INFO", help="Logging level.")

    args = p.parse_args()
    app = StateSolnApp(canonical=args.canonical)
    app.configure_logging(args.log)

    result = app.run(
        tf=args.tf, num=args.num, den=args.den, example=args.example, u=args.u,
        x0=args.x0, t0=args.t0, eval_time=args.eval, numeric=args.numeric,
        digits=args.digits, pretty=args.pretty, verify=args.verify, tol=args.tol,
        export_json=args.export_json
    )

    # Print in a deterministic order
    print(f"\n== Solution for ẋ=Ax+Bu ({args.canonical}) ==")
    print(f"A =\n{result['A']}")
    print(f"\nB =\n{result['B']}")
    print(f"\nΦ(t) =\n{result['Phi']}")
    print(f"\nx_hom =\n{result['x_hom']}")
    print(f"\nx_part =\n{result['x_part']}")
    print(f"\n   x(t) =\n{result['x']}")
    if result.get("verification"):
        print(f"\n[Verification] {result['verification']}")

if __name__ == "__main__":
    main()
