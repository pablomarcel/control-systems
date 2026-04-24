from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json

DEFAULT_IN  = Path("stateSpaceDesign/observerGainMatrixTool/in")
DEFAULT_OUT = Path("stateSpaceDesign/observerGainMatrixTool/out")

@dataclass
class OutputManager:
    out_dir: Path = DEFAULT_OUT

    def ensure(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, data, filename: str) -> Path:
        self.ensure()
        path = self.out_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return path

    def write_text(self, text: str, filename: str) -> Path:
        self.ensure()
        path = self.out_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path
