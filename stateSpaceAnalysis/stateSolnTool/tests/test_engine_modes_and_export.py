
import json, pathlib
from stateSpaceAnalysis.stateSolnTool.core import StateSolnEngine

def test_modes_and_eval_and_export(tmp_path):
    eng = StateSolnEngine(canonical="observable")
    res = eng.run(example="ogata_9_1", u="1", eval_time=1.0, pretty=False, verify=True)
    assert res["A"]
    # diagonal mode
    eng2 = StateSolnEngine(canonical="diagonal")
    res2 = eng2.run(example="ogata_9_1", u="1", pretty=True)
    assert res2["Phi"]
    # export
    out_json = tmp_path / "dump.json"
    eng2.run(example="ogata_9_1", export_json=str(out_json))
    data = json.loads(pathlib.Path(out_json).read_text())
    assert all(k in data for k in ["A","B","Phi(t)","x(t)"])
