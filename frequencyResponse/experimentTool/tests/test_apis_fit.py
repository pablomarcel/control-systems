from __future__ import annotations
from pathlib import Path
import numpy as np

from frequencyResponse.experimentTool.design import ogata_7_25
from frequencyResponse.experimentTool.apis import fit_simple_from_csv, refine_fit, ExperimentService
from frequencyResponse.experimentTool.io import make_synth_csv, read_csv

def test_fit_and_refine_pipeline(repo_root: Path):
    spec_true = ogata_7_25()
    csv_path = repo_root / "frequencyResponse" / "experimentTool" / "in" / "fit_unit.csv"
    make_synth_csv(spec_true, 0.1, 40.0, 200, str(csv_path), delay_method="frd", noise_db=0.1, noise_deg=0.2)
    diag = {}
    spec0 = fit_simple_from_csv(str(csv_path), diag)
    # Should roughly approximate the true parameters
    assert spec0.lam in (0,1,2)  # heuristic may pick 1
    # Refine and compare
    data = read_csv(str(csv_path))
    specR = refine_fit(spec0, data, "frd", diag)
    # Check refined params are reasonable
    assert specR.K > 0
    assert len(specR.poles1) == 1 and len(specR.wns) == 1 and len(specR.zetas) == 1
    # Facade quick check
    svc = ExperimentService(delay_method="frd", pade_order=6)
    specF, info = svc.fit_from_csv(str(csv_path), refine=True)
    assert "diagnostics" in info and "refined" in info
