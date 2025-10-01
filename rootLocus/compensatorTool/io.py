# modernControl/rootLocus/compensatorTool/io.py
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
from typing import Any

from .design import DesignResult

ROOT = Path(__file__).resolve().parent
IN_DIR = ROOT / "in"
OUT_DIR = ROOT / "out"
IN_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)


def save_result(result: DesignResult, stem: str) -> Path:
    out = OUT_DIR / f"{stem}.json"
    payload: dict[str, Any] = asdict(result)
    # convert TF to strings
    payload["Gc"] = str(result.Gc)
    payload["L"] = str(result.L)
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return out