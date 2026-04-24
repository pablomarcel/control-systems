
from __future__ import annotations
import json
from typing import Any, Optional
from .utils import ensure_out_path

def write_json(obj: Any, path: Optional[str], default_dir: str, default_name: str) -> Optional[str]:
    out = ensure_out_path(path, default_dir, default_name) if path is not None else None
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, default=lambda o: {"re": o.real, "im": o.imag} if isinstance(o, complex) else str(o))
    return out
