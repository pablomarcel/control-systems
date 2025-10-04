from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
from .apis import StateRepAPIRequest, StateRepService
from .io import save_json

DEFAULT_OUT = Path(__file__).resolve().parent / "out"

@dataclass
class StateRepApp:
    out_dir: Path = DEFAULT_OUT

    def run(self, req: StateRepAPIRequest, export_json: Optional[str] = None) -> Dict:
        resp = StateRepService.run(req)
        if export_json:
            out_path = self.out_dir / export_json
            save_json(resp.results, out_path)
        return resp.results
