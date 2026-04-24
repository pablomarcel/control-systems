import numpy as np
from state_space_design.lqrTool.io import parse_matrix, parse_vector, parse_Q, parse_R, build_model_from_ABCD, build_model_from_tf

def test_parse_matrix_and_vector():
    A = parse_matrix("0 1; 0 -1")
    v = parse_vector("1, 2, 3")
    assert A.shape == (2,2)
    assert v.shape == (3,1)

def test_parse_Q_variants():
    Qe = parse_Q("eye:3", 2)
    Qd = parse_Q("diag:1,2,3", 3)
    Qm = parse_Q("1 0; 0 2", 2)
    assert Qe.shape == (3,3)
    assert np.allclose(np.diag(Qd), [1,2,3])
    assert Qm.shape == (2,2)

def test_parse_R_scalar_and_matrix():
    r = parse_R("2.5")
    Rm = parse_R("1 0; 0 3")
    assert isinstance(r, float) and r == 2.5
    assert Rm.shape == (2,2)

def test_build_models_from_ABCD_and_tf():
    m1 = build_model_from_ABCD("0 1; 0 -1", "0; 1", "1 0", "0")
    assert m1.A.shape == (2,2) and m1.B.shape == (2,1) and m1.C.shape == (1,2)
    m2 = build_model_from_tf("1", "1,1")
    # should be controllable canonical SS of first-order system
    assert m2.A.shape[0] == m2.B.shape[0]
