# =============================
# File: transientAnalysis/hurwitzTool/tools/tool_plantuml.py
# =============================
from __future__ import annotations
import inspect
from types import ModuleType
from typing import Iterable


def to_plantuml(mods: Iterable[ModuleType]) -> str:
    """Generate a minimal PlantUML class diagram from modules.

    Usage:
        python -m transientAnalysis.hurwitzTool.tools.tool_plantuml > hurwitz_classes.puml
    Then render with PlantUML or kroki.
    """
    lines = ["@startuml hurwitzTool", "!pragma useIntermediatePackages false", "skinparam classAttributeIconSize 0", ""]
    seen = set()
    for m in mods:
        for name, obj in inspect.getmembers(m):
            if inspect.isclass(obj) and obj.__module__.startswith(m.__name__):
                fq = f"{obj.__module__}.{obj.__name__}"
                if fq in seen:
                    continue
                seen.add(fq)
                attrs = []
                for an, av in getattr(obj, "__annotations__", {}).items():
                    attrs.append(f"  {an}: {getattr(av, '__name__', str(av))}")
                lines.append(f"class {fq} {{")
                lines.extend(attrs)
                lines.append("}")
    lines.append("\n@enduml")
    return "\n".join(lines)

if __name__ == "__main__":  # pragma: no cover
    import transientAnalysis.hurwitzTool.core as core
    import transientAnalysis.hurwitzTool.app as app
    import transientAnalysis.hurwitzTool.apis as apis
    print(to_plantuml([core, app, apis]))