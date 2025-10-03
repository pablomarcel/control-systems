from __future__ import annotations
import os
from pathlib import Path
from typing import List

def ensure_out_dir(base: str = None) -> str:
    """Ensure the package-level out directory exists.
    Defaults to `pidControllers/pidTool/out` relative to CWD.
    """
    if base is None:
        base = os.path.join("pidControllers", "pidTool", "out")
    Path(base).mkdir(parents=True, exist_ok=True)
    return base

def parse_list_of_floats(s: str | None) -> List[float]:
    if not s:
        return []
    return [float(x) for x in s.replace(",", " ").split()]

def parse_list_of_complex(s: str | None) -> List[complex]:
    if not s:
        return []
    toks = s.replace(",", " ").replace("i", "j").split()
    return [complex(tok) for tok in toks]
