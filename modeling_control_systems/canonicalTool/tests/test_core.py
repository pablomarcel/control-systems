
# tests/test_core.py
import numpy as np
import control as ct
from modeling_control_systems.canonicalTool.core import CanonicalForms
from modeling_control_systems.canonicalTool.utils import tf_equal

def test_tf_roundtrip_equivalence():
    num = [2, 3]
    den = [1, 1, 10]
    sys_ccf = CanonicalForms.ccf_from_tf(num, den)
    sys_ocf = CanonicalForms.ocf_from_ss(sys_ccf)
    sys_modal = CanonicalForms.modal_real(sys_ccf)
    assert tf_equal(sys_ccf, sys_ocf)
    assert tf_equal(sys_ccf, sys_modal)
