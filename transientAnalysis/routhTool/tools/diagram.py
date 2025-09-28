# transientAnalysis/routhTool/tools/diagram.py
from __future__ import annotations
import inspect
from typing import Iterable, Type

def _classes_in_module(mod) -> list[type]:
    out = []
    for _, obj in inspect.getmembers(mod, inspect.isclass):
        if obj.__module__ == mod.__name__:
            out.append(obj)
    return out

def emit_plantuml(modules: Iterable[object]) -> str:
    lines = ["@startuml routhTool"]
    lines.append("!pragma useIntermediatePackages false")
    for m in modules:
        for cls in _classes_in_module(m):
            lines.append(f"class {cls.__module__}.{cls.__name__} {{}}")
    # naive associations: dataclass fields (best-effort)
    for m in modules:
        for cls in _classes_in_module(m):
            try:
                hints = getattr(cls, "__annotations__", {}) or {}
                for _, tp in hints.items():
                    if getattr(tp, "__module__", None) in [mm.__name__ for mm in modules]:
                        lines.append(f"{cls.__module__}.{cls.__name__} --> {tp.__module__}.{tp.__name__}")
            except Exception:
                pass
    lines.append("@enduml")
    return "\n".join(lines)

def emit_mermaid(modules: Iterable[object]) -> str:
    lines = ["classDiagram"]
    for m in modules:
        for cls in _classes_in_module(m):
            fq = f"{cls.__module__}.{cls.__name__}".replace(".", "_")
            lines.append(f"class {fq} {{}}")
    return "\n".join(lines)

if __name__ == "__main__":  # pragma: no cover
    # Demo usage:
    from transientAnalysis.routhTool import core, app, apis
    print(emit_plantuml([core, app, apis]))