"""Generate a lightweight PlantUML class diagram for the responseTool package.

Writes `out/response_tool_classes.puml`. Rendering is up to the user (PlantUML server, VSCode ext, etc.).
"""
from __future__ import annotations
from pathlib import Path
import inspect
import types

from .. import app as app_mod
from .. import core as core_mod

PLANTUML_HEADER = """@startuml responseTool
!pragma useIntermediatePackages false
skinparam classAttributeIconSize 0
"""

PLANTUML_FOOTER = "\n@enduml\n"


def _class_block(cls: type) -> str:
    name = f"{cls.__module__}.{cls.__name__}"
    lines = [f"class {name} {{"]
    for k, v in getattr(cls, "__annotations__", {}).items():
        lines.append(f"  {k}: {getattr(v, '__name__', str(v))}")
    lines.append("}\n")
    return "\n".join(lines)


def generate(root: Path) -> Path:
    out = [PLANTUML_HEADER]
    classes = []
    for mod in (app_mod, core_mod):
        for _, obj in inspect.getmembers(mod):
            if inspect.isclass(obj) and obj.__module__.startswith("transientAnalysis.responseTool"):
                classes.append(obj)
    for c in classes:
        out.append(_class_block(c))
    out.append(PLANTUML_FOOTER)

    path = Path(root) / "out" / "response_tool_classes.puml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(out), encoding="utf-8")
    return path