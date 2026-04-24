# SPDX-License-Identifier: MIT
from pathlib import Path
import json
import numpy as np

from state_space_design.statePlotsTool.apis import StatePlotsAPI, RunRequest

def test_step_csv(tmp_path):
    Acl = [[0,1],[-2,-3]]
    Bcl = [[0],[1]]
    C   = [[1,0]]
    D   = [[0]]
    payload = {
        "Acl": Acl, "Bcl": Bcl, "C": C, "D": D,
        "r": 1.0,
        "state_names": ["x1","x2"],
        "output_names": ["y1"]
    }
    in_file = tmp_path / "io.json"
    with open(in_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    api = StatePlotsAPI()
    req = RunRequest(
        data=in_file,
        scenario='step',
        what='y',
        t="0:0.1:0.5",
        backend='none',
        save_csv="step.csv",
        out_dir=tmp_path,
        no_show=True
    )
    res = api.run(req)
    assert res['t_len'] == 6
    csv_path = Path(res['paths']['csv'])
    assert csv_path.exists()
    txt = csv_path.read_text()
    assert 't,y1' in txt.splitlines()[0]
