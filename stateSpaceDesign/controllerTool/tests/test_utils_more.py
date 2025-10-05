# -*- coding: utf-8 -*-
import numpy as np
import control as ct
from stateSpaceDesign.controllerTool.utils import (
    parse_real_vec, parse_complex_list, mat_inline, tf_eval_jw, bode_data, tf_coeffs
)

def test_parse_helpers_and_inline():
    v = parse_real_vec("1, 2  3")
    assert v.tolist() == [1.0, 2.0, 3.0]
    c = parse_complex_list("-1+2j, -3-4j")
    assert c.shape[0] == 2
    m = mat_inline([[1, 2], [3, 4]], precision=2)
    assert m.startswith("[[") and "]]" in m

def test_tf_eval_and_bode():
    G = ct.tf([1.0], [1.0, 1.0])  # 1/(s+1)
    w = np.array([0.1, 1.0, 10.0])
    H = tf_eval_jw(G, w)
    assert H.shape == w.shape
    mag_db, ph = bode_data(G, w)
    assert mag_db.shape == w.shape and ph.shape == w.shape
    num, den = tf_coeffs(G)
    assert den.size == 2 and num.size == 1
