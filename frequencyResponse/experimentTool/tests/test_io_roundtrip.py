from __future__ import annotations
from pathlib import Path
import numpy as np
import json

from frequencyResponse.experimentTool.design import ogata_7_25
from frequencyResponse.experimentTool.io import make_synth_csv, read_csv, export_summary
from frequencyResponse.experimentTool.core import build_rational_tf, bode_arrays

def test_make_and_read_csv(repo_root: Path):
    spec = ogata_7_25()
    csv_path = repo_root / "frequencyResponse" / "experimentTool" / "in" / "unit.csv"
    out = make_synth_csv(spec, 0.1, 40.0, 64, str(csv_path), delay_method="frd", noise_db=0.0, noise_deg=0.0)
    assert Path(out).exists()
    D = read_csv(str(csv_path))
    assert set(D.keys()) == {"w","mag_db","phase_deg"}
    # Sorted ascending
    assert (np.diff(D["w"]) >= 0).all()

def test_export_summary_json(repo_root: Path):
    spec = ogata_7_25()
    G = build_rational_tf(spec)
    w = np.logspace(-1, 2, 64)
    bode = bode_arrays(G, w, spec.delay, delay_method="frd")
    # Use the rational (no Padé) system for export
    prefix = repo_root / "frequencyResponse" / "experimentTool" / "out" / "summary_unit"
    js = export_summary(str(prefix), spec, G, "frd", None, diagnostics={"ok": True})
    assert Path(js).exists()
    data = json.loads(Path(js).read_text(encoding="utf-8"))
    assert data["spec"]["K"] == 10.0  # from ogata_7_25
    assert data["delay_method"] == "frd"
    assert isinstance(data["rational_num"], list)
    assert isinstance(data["poles"], list) and isinstance(data["zeros"], list)
