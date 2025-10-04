
# app.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from .io import RulesRepository
from .core import TuningEngine, TuningResult
from .design import TuningService
from .apis import PrintAPI, ExportAPI
from .utils import TuningInputs
from .tools.tool_paths import ensure_outdir, OUT_DIR
import json
from pathlib import Path

@dataclass(slots=True)
class TuningApp:
    repo: RulesRepository
    engine: TuningEngine
    service: TuningService
    printer: PrintAPI
    exporter: ExportAPI

    @classmethod
    def create_default(cls) -> "TuningApp":
        repo = RulesRepository()
        engine = TuningEngine()
        service = TuningService(repo=repo, engine=engine)
        printer = PrintAPI()
        exporter = ExportAPI()
        return cls(repo=repo, engine=engine, service=service, printer=printer, exporter=exporter)

    def run_compute(self, *, method: str, controller: str, inputs: TuningInputs, file: str | None = None) -> TuningResult:
        return self.service.compute(method, controller, inputs, file=file)

    def save_json(self, data: dict, filename: str) -> Path:
        ensure_outdir()
        p = OUT_DIR / filename
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return p
