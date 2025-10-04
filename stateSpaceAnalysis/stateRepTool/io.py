from __future__ import annotations
from typing import Dict
from pathlib import Path
import json

def save_json(data: Dict, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return p
