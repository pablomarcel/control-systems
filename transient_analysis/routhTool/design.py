# transient_analysis/routhTool/design.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass(slots=True)
class RouthPreset:
    """Small catalog for quick demos / docs / tests."""
    name: str
    coeffs: str
    symbols: List[str] | None = None
    solve_for: str | None = None

PRESETS: list[RouthPreset] = [
    RouthPreset("cubic_numeric", "1, 5, 6, 2"),
    RouthPreset("cubic_gain", "1, 5, 6, K", symbols=["K"], solve_for="K"),
    RouthPreset("quartic_gain", "1, 2, 3, 4, K", symbols=["K"], solve_for="K"),
    RouthPreset("row_of_zeros_demo", "1, 0, 2, 0, 1"),
]