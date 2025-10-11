
# io.py
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict
from pathlib import Path
from .tools.tool_paths import IN_DIR, PKG_ROOT

class RulesLoadError(RuntimeError):
    pass

@dataclass(slots=True)
class RulesRepository:
    """Reads tuning rule JSON files from the package 'in/' folder or explicit path."""
    default_file: str = "tuning_rules.json"

    def _resolve(self, file: str | None) -> Path:
        if not file:
            return IN_DIR / self.default_file

        p = Path(file)
        if p.is_absolute():
            return p

        # Allow 'in/...' or 'out/...' relative to the package root
        if p.parts and p.parts[0] in {"in", "out"}:
            return PKG_ROOT / p

        # Otherwise, treat as a filename under in/
        return IN_DIR / p

    def read_json(self, file: str | None = None) -> Dict[str, Any]:
        path = self._resolve(file)
        if not path.exists():
            raise RulesLoadError(f"JSON file not found: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            raise RulesLoadError(f"Failed to parse JSON '{path}': {e}")
