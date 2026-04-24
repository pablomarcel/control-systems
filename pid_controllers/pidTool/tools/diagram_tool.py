from __future__ import annotations
import argparse, inspect, pkgutil, importlib, os
from pathlib import Path

def discover_classes(package_root: str = "pid_controllers.pidTool") -> list[tuple[str, str]]:
    classes: list[tuple[str, str]] = []
    pkg = importlib.import_module(package_root)
    pkg_path = Path(pkg.__file__).parent
    for mod in pkgutil.iter_modules([str(pkg_path)]):
        if mod.name in {"tests", "tools", "__pycache__"}:
            continue
        m = importlib.import_module(f"{package_root}.{mod.name}")
        for name, obj in inspect.getmembers(m, inspect.isclass):
            if getattr(obj, "__module__", "").startswith(package_root):
                classes.append((mod.name, name))
    return classes

def emit_mermaid(classes: list[tuple[str, str]]) -> str:
    lines = ["classDiagram"]
    for mod, cls in classes:
        lines.append(f"  class {cls}")  # simple nodes
    # naive: module grouping as comments
    lines.append("  %% Module grouping not rendered as packages in plain Mermaid here.")
    return "\n".join(lines) + "\n"

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-mermaid", action="store_true")
    args = ap.parse_args(argv)
    classes = discover_classes()
    if args.emit_mermaid:
        mmd = emit_mermaid(classes)
        out_dir = Path("pid_controllers/pidTool/out"); out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / "pidTool_classes.mmd"
        p.write_text(mmd, encoding="utf-8")
        print(f"[saved] Mermaid -> {p}")
    else:
        print(classes)

if __name__ == "__main__":
    main()
