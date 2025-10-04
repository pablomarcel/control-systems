
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import json, os
from .utils import ensure_dir

DEFAULT_OUT_DIR = "stateSpaceAnalysis/canonicalTool/out"

@dataclass(slots=True)
class SaveOptions:
    save_path: Optional[str] = None

def save_json(data: dict, path: str) -> None:
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def default_out_path(filename: str) -> str:
    return os.path.join(DEFAULT_OUT_DIR, filename)
