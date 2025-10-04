
# design.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .io import RulesRepository
from .core import TuningEngine, TuningResult
from .utils import TuningInputs

@dataclass(slots=True)
class TuningService:
    """High-level façade: loads rules, invokes engine, exposes helpers for printing/exporting."""
    repo: RulesRepository
    engine: TuningEngine

    def list_methods(self, file: str | None = None) -> Dict[str, str]:
        data = self.repo.read_json(file)
        return {k: v.get("name", "") for k, v in data.get("methods", {}).items()}

    def list_controllers(self, method: str, file: str | None = None) -> list[str]:
        data = self.repo.read_json(file)
        m = data["methods"][method]
        return list(m.get("controllers", {}).keys())

    def list_formulas(self, method: str, file: str | None = None) -> Dict[str, Dict[str, str]]:
        data = self.repo.read_json(file)
        m = data["methods"][method]
        out: Dict[str, Dict[str, str]] = {}
        for c, blk in m.get("controllers", {}).items():
            out[c] = blk.get("formula", {})
        return out

    def compute(self, method: str, controller: str, inputs: TuningInputs, file: str | None = None) -> TuningResult:
        data = self.repo.read_json(file)
        return self.engine.compute(data, method, controller, inputs)
