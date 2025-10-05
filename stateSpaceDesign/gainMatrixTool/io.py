from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import os, json

@dataclass
class JsonExporter:
    def export(self, payload: dict, path: str):
        out = os.path.join(os.path.dirname(path) or ".", os.path.basename(path))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Exported JSON -> {out}")

@dataclass
class BatchReader:
    def from_csv(self, path: str) -> List[Dict[str, Any]]:
        import csv
        with open(path, "r", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            return [row for row in rdr]

    def from_yaml(self, path: str) -> List[Dict[str, Any]]:
        try:
            import yaml
        except Exception as e:
            raise SystemExit("Install pyyaml to use YAML files") from e
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict) and "cases" in data:
            return data["cases"]
        if isinstance(data, list):
            return data
        raise SystemExit("YAML structure must be a list or a dict with key 'cases'")
