from __future__ import annotations
from typing import Dict, Any, List
from dataclasses import dataclass
from .design import DesignService
from .core import GainMatrixDesigner, parse_matrix
from .io import BatchReader, JsonExporter

@dataclass
class GainMatrixAPI:
    """Public API surface for app/tests/CLI."""
    design: DesignService
    io_reader: BatchReader
    exporter: JsonExporter

    @classmethod
    def default(cls):
        return cls(
            design=DesignService(GainMatrixDesigner()),
            io_reader=BatchReader(),
            exporter=JsonExporter()
        )

    def single(self, **kwargs) -> Dict[str, Any]:
        return self.design.run_single(**kwargs)

    def batch(self, cases, export_dir: str, verify: bool, pretty: bool):
        from tqdm import tqdm
        import os, json
        os.makedirs(export_dir, exist_ok=True)
        for case in tqdm(cases, desc="Batch"):
            name = case.get("name", "case")
            mode = case["mode"].upper()
            method = case.get("method","auto")
            payload = self.design.run_single(
                mode=mode,
                A=case["A"],
                B=case.get("B"),
                C=case.get("C"),
                poles=case["poles"],
                method=method,
                verify=verify,
                pretty=pretty
            )
            suffix = {"K":"K","L":"L","KI":"KI"}[mode]
            out = f"{export_dir}/{name}_{suffix}.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Exported JSON -> {out}")
