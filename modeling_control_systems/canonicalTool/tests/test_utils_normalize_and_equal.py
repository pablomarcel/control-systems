
import numpy as np
import control as ct
from modeling_control_systems.canonicalTool.utils import normalize_tf_coeffs, tf_equal

def test_normalize_tf_coeffs_leading_zeros_and_padding():
    num, den = normalize_tf_coeffs([1, 2], [0, 0, 2, 4])  # leading zeros in den
    assert np.allclose(den, [1, 2])  # 2,4 normalized -> 1,2
    assert np.allclose(num, [0.5, 1.0])  # 1,2 / 2

    # short numerator should be left-padded to match len(den)
    num2, den2 = normalize_tf_coeffs([3], [1, 0, 2])
    assert len(num2) == len(den2) == 3
    assert np.allclose(den2, [1, 0, 2])
    assert np.allclose(num2, [0, 0, 3])  # padded on the left

def test_tf_equal_true_for_equivalent():
    g1 = ct.TransferFunction([2,3], [1,1,10])
    g2 = ct.TransferFunction([1, 1.5], [0.5, 0.5, 5])  # scaled version
    sys1 = ct.tf2ss(g1)
    sys2 = ct.tf2ss(g2)
    assert tf_equal(sys1, sys2)
