from __future__ import annotations
import os, json
from dataclasses import dataclass

@dataclass(slots=True)
class IOConfig:
    in_dir: str = "frequencyResponse/plotTool/in"
    out_dir: str = "frequencyResponse/plotTool/out"

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)
    return p

def save_json(path: str, payload: dict):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path
