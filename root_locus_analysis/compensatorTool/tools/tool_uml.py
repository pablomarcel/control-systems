# modernControl/root_locus_analysis/compensatorTool/tools/tool_uml.py
"""Emit Mermaid and PlantUML class diagrams (no Graphviz required)."""
from __future__ import annotations
import inspect
from typing import List, Type
from dataclasses import is_dataclass

from ..design import DesignResult
from ..core import LeadStage
from ..apis import CompensatorService, PoleSpec
from ..app import CompensatorApp


def _class_sig(cls: Type) -> str:
    fields = []
    if is_dataclass(cls):
        for f in getattr(cls, "__dataclass_fields__", {}).values():
            fields.append(f"  + {f.name}: {getattr(f.type, '__name__', f.type)}")
    return "\n".join(fields)


def mermaid() -> str:
    lines = ["classDiagram"]
    for cls in (LeadStage, DesignResult, CompensatorService, PoleSpec, CompensatorApp):
        name = cls.__name__
        lines.append(f"class {name} {{")
        sig = _class_sig(cls)
        if sig:
            lines.append(sig)
        lines.append("}")
    lines += [
        "CompensatorService --> DesignResult",
        "CompensatorApp --> CompensatorService",
        "DesignResult *-- LeadStage",
        "CompensatorService --> PoleSpec",
    ]
    return "\n".join(lines)


def plantuml() -> str:
    lines = ["@startuml compensatorTool"]
    for cls in (LeadStage, DesignResult, CompensatorService, PoleSpec, CompensatorApp):
        name = cls.__name__
        lines.append(f"class {name} {{")
        sig = _class_sig(cls)
        if sig:
            lines.append(sig)
        lines.append("}")
    lines += [
        "CompensatorService --> DesignResult",
        "CompensatorApp --> CompensatorService",
        "DesignResult *-- LeadStage",
        "CompensatorService --> PoleSpec",
        "@enduml",
    ]
    return "\n".join(lines)