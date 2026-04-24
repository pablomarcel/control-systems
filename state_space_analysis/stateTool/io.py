from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict
import json
from pathlib import Path

def out_path(rel: str = "state_space_analysis/stateTool/out") -> Path:
    p = Path(rel)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_json(obj: Dict[str, Any], filename: str) -> str:
    p = out_path() / filename
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    return str(p)
