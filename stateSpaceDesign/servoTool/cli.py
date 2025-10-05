from __future__ import annotations
import argparse
from .apis import RunRequest, run

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="servoTool",
        description="Servo I/O model builder (OOP refactor of servos.py)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    ap.add_argument("--data", required=True, help="Controller JSON from gain_matrix.py (mode=K or KI)")
    ap.add_argument("--C", help="Output C (needed for mode=K if not present in JSON)")
    ap.add_argument("--r", type=float, default=1.0, help="Reference step amplitude")
    ap.add_argument("--k_r", type=float, default=None, help="Override prefilter for mode=K")
    ap.add_argument("--t", default="0:0.01:5", help="Time vector (e.g., '0:0.01:5' or '0,1,2')")
    ap.add_argument("--save_csv", default=None, help="If set, simulate step and save CSV to stateSpaceDesign/servoTool/out/")
    ap.add_argument("--export_json", default=None, help="Export IO JSON to stateSpaceDesign/servoTool/out/")
    ap.add_argument("--backend", choices=["none","mpl","plotly","both"], default="none",
                    help="Optional quick-look plotting")
    ap.add_argument("--no_show", action="store_true", help="Do not pop up windows")
    return ap

def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)

    req = RunRequest(
        data_path=args.data,
        mode_C=args.C,
        r=args.r,
        k_r_override=args.k_r,
        t=args.t,
        save_csv=args.save_csv,
        export_json=args.export_json,
        backend=args.backend,
        no_show=args.no_show,
    )
    resp = run(req)

    # Friendly console messages
    print("\n== ServoTool results ==")
    print(f"mode: {resp.model.mode.value}, r: {resp.model.r}")
    if resp.model.k_r is not None:
        print(f"k_r: {resp.model.k_r:g}")
    if resp.model.kI is not None:
        print(f"kI: {resp.model.kI:g}")
    if resp.io_json_path:
        print(f"JSON: {resp.io_json_path}")
    if resp.csv_path:
        print(f"CSV : {resp.csv_path}")
    if resp.plot_html_path:
        print(f"Plot: {resp.plot_html_path}")

if __name__ == "__main__":
    main()
