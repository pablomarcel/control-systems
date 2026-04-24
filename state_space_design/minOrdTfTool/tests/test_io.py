
import numpy as np, pathlib
from state_space_design.minOrdTfTool.io import export_json, pretty_dump

def test_export_json_and_pretty_dump(tmp_path):
    payload = {
        "A": np.eye(2).tolist(),
        "B": [[0],[1]],
        "C": [[1,0]],
        "tf_num": [1.0, 2.0, 3.0],
        "tf_den": [1.0, 4.0, 5.0],
        "misc": {"note": "ok"}
    }
    out = tmp_path/"p.json"
    p = export_json(payload, str(out))
    assert out.exists() and str(out) == p
    txt = pretty_dump(payload, precision=4)
    assert "A:" in txt and "tf_den" in txt
