
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import inspect

@dataclass(slots=True)
class ClassInfo:
    name: str
    bases: list[str]

def discover_classes(modules: Iterable[object]) -> list[ClassInfo]:
    infos: list[ClassInfo] = []
    for m in modules:
        for _, cls in inspect.getmembers(m, inspect.isclass):
            if cls.__module__.startswith(m.__name__):
                bases = [b.__name__ for b in getattr(cls, '__mro__', [])[1:] if b.__name__ != 'object']
                infos.append(ClassInfo(name=cls.__name__, bases=bases))
    return infos

def as_mermaid(infos: list[ClassInfo]) -> str:
    lines = ['classDiagram']
    for ci in infos:
        lines.append(f'  class {ci.name}')
        for b in ci.bases:
            lines.append(f'  {b} <|-- {ci.name}')
    return '\\n'.join(lines)
