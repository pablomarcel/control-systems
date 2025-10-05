
from __future__ import annotations
import pytest
import control as ct
from stateSpaceAnalysis.canonicalTool.core import CanonicalFormsEngine as Eng

def test_normalize_leading_zeros_and_error():
    n, d = Eng.normalize_tf_coeffs([0,2,3], [0,1,1,10])
    assert d[0] == pytest.approx(1.0)
    with pytest.raises(ValueError):
        Eng.normalize_tf_coeffs([1,2], [0,0,0])

def test_tf_equal_false_case():
    n1, d1 = Eng.normalize_tf_coeffs([1], [1,1])
    n2, d2 = Eng.normalize_tf_coeffs([2], [1,2])
    sys1 = Eng.make_ccf_from_tf(n1, d1)
    sys2 = Eng.make_ccf_from_tf(n2, d2)
    assert not Eng.tf_equal(sys1, sys2)

def test_modal_real_smoke():
    n, d = Eng.normalize_tf_coeffs([1], [1,2,2])
    sys = Eng.make_ccf_from_tf(n, d)
    mod = Eng.make_modal_real(sys)
    assert isinstance(mod, ct.StateSpace)
