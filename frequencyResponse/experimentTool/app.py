from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

from .design import ModelSpec, ogata_7_25
from .apis import ExperimentService, fit_simple_from_csv, refine_fit
from .core import build_rational_tf, bode_arrays
from .io import read_csv, save_bode_csv, export_summary, make_synth_csv
from .utils import ensure_in_dir, ensure_out_dir, set_verbose, info

@dataclass(slots=True)
class ExperimentApp:
    root: Path
    delay_method: str = "frd"
    pade_order: int = 6

    @property
    def in_dir(self) -> Path:
        return Path(ensure_in_dir(self.root))

    @property
    def out_dir(self) -> Path:
        return Path(ensure_out_dir(self.root))

    def preset(self) -> ModelSpec:
        return ogata_7_25()

    def run(self, spec: ModelSpec, *, wmin: float, wmax: float, npts: int) -> dict:
        svc = ExperimentService(delay_method=self.delay_method, pade_order=self.pade_order)
        sys_for_freq, bode = svc.bode_for(spec, wmin, wmax, npts)
        return {"sys": sys_for_freq, "bode": bode}

    def synth_csv(self, spec: ModelSpec, *, wmin: float, wmax: float, npts: int,
                  csv_out: str, noise_db: float = 0.0, noise_deg: float = 0.0) -> str:
        return make_synth_csv(spec, wmin, wmax, npts, csv_out, self.delay_method, noise_db, noise_deg)
