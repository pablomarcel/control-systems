
from __future__ import annotations
import numpy as np
import control as ct
from frequency_response.compensatorTool import core as C

def test_tf_arrays_and_eval_L():
    G = ct.tf([1.0], [1.0, 1.0])
    n, d = C.tf_arrays(G)
    assert list(n) == [1.0]
    assert len(d) == 2
    w = np.array([0.1, 1.0, 10.0])
    Hjw = C.eval_L(G, w)
    assert Hjw.shape == w.shape

def test_frequency_response_arrays_fallback():
    # Should work for TF and return squeezed arrays
    G = ct.tf([1.0], [1.0, 1.0])
    w = np.logspace(-2, 2, 32)
    mag, ph, ww = C.frequency_response_arrays(G, w)
    assert mag.shape == w.shape
    assert ph.shape == w.shape
    assert ww.shape == w.shape

def test_get_margins_and_is_stable():
    G = ct.tf([1.0], [1.0, 1.0])
    gm, pm, wgm, wpm = C.get_margins(G)
    # Just sanity: types are floats (may be nan depending on plant)
    assert all(isinstance(v, float) for v in [gm, pm, wgm, wpm])
    assert C.is_stable(ct.feedback(G, 1))

def test_kv_and_scaling_type1():
    # Type-1 system: 1/(s*(s+1))
    G = ct.tf([1.0], [1.0, 1.0, 0.0])
    Kv_old = C.kv_of_tf(G)
    assert Kv_old > 0
    G2, Kscale, Kv_old_check = C.set_gain_for_Kv(G, Kv_old*2)
    assert Kscale == 2
    assert isinstance(G2, type(G))

def test_nichols_templates_shapes():
    M_lines, N_lines = C.nichols_templates([-12, 0, 6], [-60, -120])
    assert len(M_lines) == 3
    assert len(N_lines) == 2
    for phs,gdbs,name in M_lines + N_lines:
        assert len(phs) == len(gdbs)
        assert isinstance(name, str)
