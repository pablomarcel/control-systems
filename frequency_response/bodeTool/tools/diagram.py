from __future__ import annotations
import inspect
from .. import app, apis, core, design

def emit_puml() -> str:
    modules = [app, apis, core, design]
    classes = []
    for m in modules:
        for name, obj in inspect.getmembers(m, inspect.isclass):
            if obj.__module__.startswith(m.__name__):
                classes.append(obj)

    lines = ["@startuml bodeTool", "!pragma useIntermediatePackages false", ""]
    for cls in classes:
        lines.append(f"class {cls.__module__}.{cls.__name__} {{}}")
    lines += [
        "frequency_response.bodeTool.app.BodeApp --> frequency_response.bodeTool.core.TFBuilder",
        "frequency_response.bodeTool.app.BodeApp --> frequency_response.bodeTool.core.FrequencyGrid",
        "frequency_response.bodeTool.app.BodeApp --> frequency_response.bodeTool.core.Analyzer",
        "frequency_response.bodeTool.design.BodePlotter --> frequency_response.bodeTool.core.Analyzer",
    ]
    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)
