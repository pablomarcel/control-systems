from __future__ import annotations
import os, json
from dataclasses import dataclass, field

def _pkg_dir() -> str:
    # Directory that contains this file: .../frequency_response/plotTool
    return os.path.dirname(os.path.abspath(__file__))

@dataclass(slots=True)
class IOConfig:
    # Default I/O dirs live INSIDE the plotTool package folder
    in_dir: str  = field(default_factory=lambda: os.path.join(_pkg_dir(), "in"))
    out_dir: str = field(default_factory=lambda: os.path.join(_pkg_dir(), "out"))

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)
    return p

def save_json(path: str, payload: dict):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path
