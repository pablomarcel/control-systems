
# cli.py
from __future__ import annotations
import argparse, sys, csv, json, os

# ---------- Import shim so `python cli.py` works with absolute imports ----------
if __package__ in (None, ""):
    # Running as a script: add project root to sys.path and import absolute modules
    _pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _pkg_root not in sys.path:
        sys.path.insert(0, _pkg_root)

    from pidControllers.tuningTool.app import TuningApp
    from pidControllers.tuningTool.utils import TuningInputs
    from pidControllers.tuningTool.tools.tool_paths import OUT_DIR, ensure_outdir
else:
    # Normal package execution
    from .app import TuningApp
    from .utils import TuningInputs
    from .tools.tool_paths import OUT_DIR, ensure_outdir

def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pidControllers.tuningTool", description="Query PID tuning rules (Ziegler–Nichols, extendable).")
    ap.add_argument("--file", default="tuning_rules.json", help="Rules JSON file. If relative, resolved under pidControllers/tuningTool/in.")
    ap.add_argument("--method", help="Method key in JSON (e.g., ZN_step, ZN_ultimate, CC_step).")
    ap.add_argument("--controller", help="Controller key in JSON (e.g., P, PI, PID).")
    # Inputs are optional flags; validation is driven by JSON's methods[...]['inputs']
    ap.add_argument("--L", type=float, help="Process dead time L.")
    ap.add_argument("--T", type=float, help="Process time constant T.")
    ap.add_argument("--Kcr", type=float, help="Critical gain Kcr.")
    ap.add_argument("--Pcr", type=float, help="Critical period Pcr.")
    ap.add_argument("--precision", type=int, default=6, help="Digits for printed floats.")
    ap.add_argument("--list", choices=["methods", "controllers", "formulas"], help="List available items (optionally combine with --method).")
    ap.add_argument("--export-json", help="Write result JSON to pidControllers/tuningTool/out/<name>.json")
    ap.add_argument("--export-csv", help="Write result CSV to pidControllers/tuningTool/out/<name>.csv")
    return ap

def _validate_required_inputs(app: TuningApp, args) -> tuple[bool, str]:
    # Load the JSON and fetch required inputs list for the method
    data = app.repo.read_json(args.file)
    if args.method not in data.get("methods", {}):
        return False, f"Unknown method '{args.method}'. Try --list methods."
    req = list(data["methods"][args.method].get("inputs", []))
    missing = [name for name in req if getattr(args, name, None) is None]
    if missing:
        return False, f"Method '{args.method}' requires inputs: {', '.join(req)}. Missing: {', '.join(missing)}."
    # Also check controller exists under method
    if args.controller not in data["methods"][args.method].get("controllers", {}):
        return False, f"Unknown controller '{args.controller}' for method '{args.method}'. Try --list controllers --method {args.method}."
    return True, ""

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    ap = _build_parser()
    args = ap.parse_args(argv)

    app = TuningApp.create_default()

    if args.list:
        if args.list == "methods":
            d = app.service.list_methods(file=args.file)
            for k, v in d.items():
                print(f"{k}: {v}")
            return 0
        if args.list == "controllers":
            if not args.method:
                print("Use --method with --list controllers")
                return 2
            try:
                lst = app.service.list_controllers(args.method, file=args.file)
            except KeyError as e:
                print(str(e))
                return 2
            print("Controllers:", ", ".join(lst))
            return 0
        if args.list == "formulas":
            if not args.method:
                print("Use --method with --list formulas")
                return 2
            try:
                d = app.service.list_formulas(args.method, file=args.file)
            except KeyError as e:
                print(str(e))
                return 2
            for c, f in d.items():
                print(f"{c}: Kp={f.get('Kp')}, Ti={f.get('Ti')}, Td={f.get('Td')}")
            return 0

    if not (args.method and args.controller):
        print("Nothing to do. Provide --method and --controller, or use --list.")
        return 0

    ok, msg = _validate_required_inputs(app, args)
    if not ok:
        print(msg)
        return 2

    inputs = TuningInputs(L=args.L, T=args.T, Kcr=args.Kcr, Pcr=args.Pcr)
    res = app.run_compute(method=args.method, controller=args.controller, inputs=inputs, file=args.file)

    # Late import to avoid cycles in shim mode
    if __package__ in (None, ""):
        from pidControllers.tuningTool.apis import PrintAPI, ExportAPI
    else:
        from .apis import PrintAPI, ExportAPI

    text = PrintAPI().render_text(res, precision=args.precision)
    print(text)

    if args.export_json or args.export_csv:
        ensure_outdir()
        if args.export_json:
            data = ExportAPI().to_json(res)
            (OUT_DIR / args.export_json).write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"Saved JSON → {OUT_DIR / args.export_json}")
        if args.export_csv:
            fields = ["method", "controller", "Kp", "Ti", "Td", "Ki", "Kd"]
            with (OUT_DIR / args.export_csv).open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(fields)
                w.writerow([res.method, res.controller, res.Kp, res.Ti, res.Td, res.Ki, res.Kd])
            print(f"Saved CSV  → {OUT_DIR / args.export_csv}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
