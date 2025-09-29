# ---------------------------------
# File: transientAnalysis/icTool/tools/diagram.py
# ---------------------------------
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Type
import inspect

# Minimalist tracing decorator reused by utils.track

def track(src: str, dst: str):  # pragma: no cover (behavioral, not logic)
    def deco(fn):
        def wrapper(*a, **k):
            # no-op; hook for future logging
            return fn(*a, **k)
        wrapper.__name__ = fn.__name__
        return wrapper
    return deco


@dataclass(slots=True)
class DiagramTool:
    """Emit PlantUML and Mermaid class diagrams without external deps.

    Usage:
        from transientAnalysis.icTool import core, app, apis
        txt = DiagramTool.from_modules([core, app, apis]).emit_plantuml("icTool")
    """
    classes: list[Type]

    @staticmethod
    def from_modules(modules: Iterable[object]) -> "DiagramTool":
        classes: list[Type] = []
        for m in modules:
            for _, obj in inspect.getmembers(m, inspect.isclass):
                if obj.__module__.startswith("transientAnalysis.icTool"):
                    classes.append(obj)
        return DiagramTool(classes=classes)

    def emit_plantuml(self, name: str) -> list[str]:  # list[str] lines for easy testing
        out: list[str] = ["@startuml " + name, "!pragma useIntermediatePackages false", ""]
        for cls in self.classes:
            qual = f"{cls.__module__}.{cls.__name__}"
            out.append(f"class {qual} {{")
            # slots or annotations for fields
            ann = getattr(cls, "__annotations__", {})
            for k, v in ann.items():
                out.append(f"  {k}: {getattr(v, '__name__', str(v))}")
            out.append("}")
        out.append("@enduml\n")
        return out

    def emit_mermaid(self, name: str) -> list[str]:
        out: list[str] = ["classDiagram",]
        for cls in self.classes:
            qual = f"{cls.__module__}.{cls.__name__}"
            out.append(f"class \"{qual}\" {{")
            ann = getattr(cls, "__annotations__", {})
            for k, v in ann.items():
                out.append(f"  +{k} : {getattr(v, '__name__', str(v))}")
            out.append("}")
        return out