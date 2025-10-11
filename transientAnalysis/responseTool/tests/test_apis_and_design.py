
from __future__ import annotations
import numpy as np
from transientAnalysis.responseTool.apis import ramp_ss_api, lsim_tf_api
from transientAnalysis.responseTool.design import Presets

def test_apis_and_presets(tmp_path):
    ss = Presets.ogata_ss_simple()
    res = ramp_ss_api(ss.A, ss.B, ss.C, ss.D, tfinal=0.2, dt=0.02, root=tmp_path)
    assert res.T.size and res.y.size

    tf = Presets.ogata_tf_ex56()
    res2 = lsim_tf_api(tf.num, tf.den, u="ramp", tfinal=0.2, dt=0.02, root=tmp_path)
    assert res2.T.size and res2.y.size and res2.u.size
