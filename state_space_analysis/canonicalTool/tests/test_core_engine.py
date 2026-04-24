
from __future__ import annotations
import control as ct
from state_space_analysis.canonicalTool.core import CanonicalFormsEngine as Eng

def test_normalize_and_tf_equal():
    num = [2, 3]
    den = [1, 1, 10]
    n, d = Eng.normalize_tf_coeffs(num, den)
    assert abs(d[0] - 1.0) < 1e-12

    sys_ccf = Eng.make_ccf_from_tf(n, d)
    sys_ocf = Eng.make_ocf_from_ss(sys_ccf)
    sys_modal = Eng.make_modal_real(sys_ccf)

    assert Eng.tf_equal(sys_ccf, sys_ocf)
    assert Eng.tf_equal(sys_ccf, sys_modal)
