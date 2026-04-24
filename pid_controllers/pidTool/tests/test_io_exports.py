
import json, csv, tempfile, os, pytest
try:
    import control as ct
except Exception:
    ct = None

from pid_controllers.pidTool.io import export_results
from pid_controllers.pidTool.core import Candidate, Metrics

@pytest.mark.skipif(ct is None, reason="python-control not installed")
def test_export_results(tmp_path):
    Gp = ct.tf([1],[1,1])
    m = Metrics(overshoot=1, settling_time=2, rise_time=0.5, ess=0, itae=0.1, ise=0.2, tfinal_used=5)
    cand = Candidate(params={"K":1.0,"a":0.5}, metrics=m, obj=0.1, stable=True, controller_str="Gc")
    export_results(prefix="t", Gp=Gp, structure="pid_dz", cands=[cand], top=1, want_json=True, want_csv=True, out_dir=str(tmp_path))
    assert (tmp_path / "t_results.json").exists()
    assert (tmp_path / "t_results.csv").exists()
    # quick check JSON schema fragment
    data = json.loads((tmp_path / "t_results.json").read_text())
    assert data["structure"] == "pid_dz"
    assert data["top"] == 1
