
import numpy as np
import control as ct
from state_space_design.regulatorTool import utils

def test_parse_and_print_helpers():
    v = utils.parse_real_vec("1, 2 3")
    assert v.tolist() == [1.0, 2.0, 3.0]
    c = utils.parse_complex_list("-1+2j, -1-2j, -5")
    assert c.shape == (3,)
    s = utils.array2str(np.eye(2))
    assert "[" in s and "]" in s
    m = utils.mat_inline(np.eye(2))
    assert m.startswith("[[") and m.endswith("]]")

def test_poly_phi_and_bode():
    A = np.array([[0,1],[-2,-3]], float)
    roots = np.array([-1,-2], complex)
    coeff = utils.poly_from_roots(roots)
    Phi = utils.phi_of_A(A, coeff)
    assert Phi.shape == (2,2)
    # Use numerator length >= 2 so np.polyval sees an iterable
    G = ct.tf([1, 0],[1,1])
    w = np.logspace(-2,1,40)
    H = utils.tf_eval_jw(G,w)
    assert H.shape == w.shape
    mag, ph = utils.bode_data(G,w)
    assert mag.size == w.size and ph.size == w.size

def test_root_locus_helpers():
    # Simple 2nd order, should be stable
    G = ct.tf([1],[1,2,1])
    r,k = utils.rlocus_from_control(G, None)
    assert r.ndim == 2 and k.size > 0
