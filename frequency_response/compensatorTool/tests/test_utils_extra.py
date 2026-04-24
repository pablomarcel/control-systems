
from __future__ import annotations
import math
import numpy as np
from frequency_response.compensatorTool import utils as U

def test_db_and_undb_roundtrip():
    vals = np.array([1e-6, 1.0, 10.0])
    dbv = U.db(vals)
    back = U.undb(dbv)
    # Near-equality except for tiny floor at EPS
    assert np.allclose(vals, back, rtol=1e-6, atol=1e-12)

def test_parse_list_floats_variants():
    assert U.parse_list_floats(None) is None
    assert U.parse_list_floats([1,2,3]) == [1.0,2.0,3.0]
    assert U.parse_list_floats("1.2, 0.9  3") == [1.2, 0.9, 3.0]
    assert U.parse_list_floats("   ") is None

def test_parse_params_and_eval():
    p = U.parse_params("K=4,T=0.2, K2=K*2, W=sin(pi/2)")
    assert p["K"] == 4.0
    assert math.isclose(p["T"], 0.2)
    assert math.isclose(p["K2"], 8.0)
    assert math.isclose(p["W"], 1.0)

def test_tf_from_expr_basic():
    G = U.tf_from_expr("1/(s*(s+1))", {})
    # Should be a control.TransferFunction-like object with 2 poles
    import control as ct
    num, den = ct.tfdata(G)
    assert len(den[0][0]) == 3  # s^2 + s + 0
