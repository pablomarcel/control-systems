# =============================
# File: transient_analysis/hurwitzTool/io.py
# =============================
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import numpy as np

@dataclass(slots=True)
class IOManager:
    base_dir: Path

    @property
    def in_dir(self) -> Path:
        p = self.base_dir / "in"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def out_dir(self) -> Path:
        p = self.base_dir / "out"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def save_csv(self, path: Path, header: list[str], rows: list[list[object]]) -> Path:
        import csv
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    def save_png_heatmap(self, path: Path, xs: np.ndarray, ys: np.ndarray, Z: np.ndarray) -> str:
        try:
            import matplotlib.pyplot as plt
        except Exception as e:
            return f"(PNG not saved: matplotlib not available: {e})"
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.figure()
        plt.imshow(Z.astype(int), origin='lower', extent=[xs.min(), xs.max(), ys.min(), ys.max()],
                   aspect='auto', interpolation='nearest')
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Hurwitz stability (1=stable, 0=unstable)")
        plt.colorbar()
        plt.tight_layout()
        try:
            plt.savefig(path, dpi=160)
            plt.close()
            return f"Saved PNG -> {path}"
        except Exception as e:
            return f"(PNG save failed: {e})"