
import numpy as np
import types
import control as ct
from control_systems.canonicalTool.utils import canonical_form_safe

class FakeSys:
    def __init__(self, n=2):
        self.A = np.eye(n)
        self.B = np.zeros((n,1))
        self.C = np.zeros((1,n))
        self.D = np.zeros((1,1))

def test_canonical_form_safe_three_tuple(monkeypatch):
    fake = FakeSys()
    T = np.eye(2)
    Ti = np.eye(2)
    sys_cf = ct.ss(fake.A, fake.B, fake.C, fake.D)
    monkeypatch.setattr(ct, "canonical_form", lambda sys, form=None: (T, Ti, sys_cf))
    s, TT, TI = canonical_form_safe(sys_cf, form="observable")
    assert s is sys_cf and np.allclose(TT, T) and np.allclose(TI, Ti)

def test_canonical_form_safe_two_tuple_sys_then_T(monkeypatch):
    fake = FakeSys()
    T = np.array([[1.0,0.0],[0.0,1.0]])
    sys_cf = ct.ss(fake.A, fake.B, fake.C, fake.D)
    monkeypatch.setattr(ct, "canonical_form", lambda sys, form=None: (sys_cf, T))
    s, TT, TI = canonical_form_safe(sys_cf, form="observable")
    assert s is sys_cf and np.allclose(TT, T) and np.allclose(TI, np.linalg.inv(T))

def test_canonical_form_safe_one_value_sys(monkeypatch):
    fake = FakeSys()
    sys_cf = ct.ss(fake.A, fake.B, fake.C, fake.D)
    monkeypatch.setattr(ct, "canonical_form", lambda sys, form=None: sys_cf)
    s, TT, TI = canonical_form_safe(sys_cf, form="modal")
    assert s is sys_cf and TT.shape == TI.shape == (2,2)
