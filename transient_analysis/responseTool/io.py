from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import json
import numpy as np
import matplotlib.pyplot as plt

@dataclass(slots=True)
class IOConfig:
    in_dir: Path
    out_dir: Path

    def ensure(self):
        self.in_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        return self


def save_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path


def save_plot(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path)
    return path


def dump_ndarray(path: Path, arr: np.ndarray) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, arr)
    return path