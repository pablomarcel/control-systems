
import numpy as np
import control as ct
from modeling_control_systems.canonicalTool.core import CanonicalForms
from modeling_control_systems.canonicalTool.utils import canonical_form_safe
import modeling_control_systems.canonicalTool.utils as utils

def test_modal_fallback_real_schur(monkeypatch):
    # Force canonical_form_safe to raise so we hit the Schur fallback
    monkeypatch.setattr(utils, "canonical_form_safe", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail")))
    g = ct.TransferFunction([1],[1,1,10])
    sys = ct.tf2ss(g)
    mod = CanonicalForms.modal_real(sys)
    # Real Schur form should be upper quasi-triangular (still real) with same shape
    assert np.isrealobj(mod.A)
    assert mod.A.shape == sys.A.shape
