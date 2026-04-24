from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

@dataclass
class MinOrdRunRequest:
    A: str
    C: str
    poles: list[str]  # tokens
    B: str | None = None
    K: str | None = None
    K_poles: list[str] | None = None
    allow_pinv: bool = False
    pretty: bool = False
    precision: int = 4
    export_json: str | None = None
    verbose: bool = False

@dataclass
class MinOrdRunResult:
    json_path: str | None = None
    payload: dict = field(default_factory=dict)
