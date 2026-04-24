import json, csv, os
import control as ct
from pid_controllers.pidTool.io import export_results
from pid_controllers.pidTool.core import Candidate, Metrics

def test_export_results_files(tmp_path):
    s = ct.TransferFunction.s
    Gp = 1/(s+1)
    c = Candidate(params={"K":1.0,"a":1.0},
                  metrics=Metrics(1,1,0.1,0.0,0.1,0.2,2.0),
                  obj=0.0, stable=True, controller_str="Gc")
    export_results(prefix="io_extra", Gp=Gp, structure="pid_dz",
                   cands=[c], top=1, want_json=True, want_csv=True,
                   out_dir=str(tmp_path))
    assert (tmp_path/"io_extra_results.json").exists()
    assert (tmp_path/"io_extra_results.csv").exists()
