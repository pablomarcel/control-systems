import numpy as np
import os
os.environ["MPLBACKEND"] = "Agg"

from transientAnalysis.icTool.apis import (
    compare1_api, compare2_api, case1_api, case2_api,
    tf_step_api_from_mbk, tf_step_api_generic,
)

def test_compare_and_case_apis_basic():
    A = np.array([[0,1],[-6,-5]], float)
    C = np.eye(2)
    x0 = np.array([0.2, 0.1], float)

    r1 = compare1_api(A, x0, tfinal=0.1, dt=0.01)
    assert r1.ok and "compare" in r1.data

    r2 = compare2_api(A, C, x0, tfinal=0.1, dt=0.01)
    assert r2.ok and "compare" in r2.data

    r3 = case1_api(A, x0, tfinal=0.1, dt=0.01)
    assert r3.ok and "case1" in r3.data

    r4 = case2_api(A, C, x0, tfinal=0.1, dt=0.01)
    assert r4.ok and "case2" in r4.data

def test_tf_step_apis():
    r5 = tf_step_api_from_mbk(1.0, 3.0, 2.0, 0.1, 0.05, tfinal=0.1, dt=0.01)
    assert r5.ok and "tf_step" in r5.data

    r6 = tf_step_api_generic(np.array([0.1, 0.05, 0.0]), np.array([1.0, 3.0, 2.0]), tfinal=0.1, dt=0.01)
    assert r6.ok and "tf_step" in r6.data