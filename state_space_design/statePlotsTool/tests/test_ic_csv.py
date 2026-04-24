# SPDX-License-Identifier: MIT
from pathlib import Path
import json
import numpy as np

from state_space_design.statePlotsTool.apis import StatePlotsAPI, RunRequest
from state_space_design.statePlotsTool.utils import DEFAULT_IN_DIR, DEFAULT_OUT_DIR

def test_ic_csv(tmp_path):
    # Simple stable A with mode K (B and K produce same Acl as A-BK)
    A = [[0,1],[-2,-3]]
    B = [[0],[1]]
    K = [[0,0]]  # no change
    payload = {
        "mode": "K",
        "A": A, "B": B, "K": K,
        "state_names": ["x1","x2"]
    }
    in_file = tmp_path / "controller.json"
    with open(in_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    api = StatePlotsAPI()
    req = RunRequest(
        data=in_file,
        scenario='ic',
        x0="1 0",
        t="0:0.1:0.5",
        backend='none',
        save_csv="ic.csv",
        no_show=True,
        out_dir=tmp_path
    )
    res = api.run(req)
    assert res['t_len'] == 6
    csv_path = Path(res['paths']['csv'])
    assert csv_path.exists()
    # load back and check header length (t + 2 states)
    txt = csv_path.read_text()
    assert 't,x1,x2' in txt.splitlines()[0]
