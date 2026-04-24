from __future__ import annotations
import numpy as np
import control as ct

from frequency_response.experimentTool.design import ModelSpec, ogata_7_25
from frequency_response.experimentTool.core import build_rational_tf, bode_arrays, pretty_tf

def test_modelspec_clean_and_preset():
    s = ogata_7_25()
    s.clean()
    assert s.K == 10.0 and s.lam == 1
    assert s.zeros == [2.0] and s.poles1 == [1.0]
    assert s.wns == [8.0] and s.zetas == [0.5]
    assert s.delay == 0.2

def test_build_tf_and_bode_basic():
    s = ModelSpec(K=2.0, lam=1, zeros=[2.0], poles1=[1.0], wns=[5.0], zetas=[0.7], delay=0.1)
    G = build_rational_tf(s)
    assert isinstance(G, ct.TransferFunction)
    # Numerator/denominator exist
    assert len(G.num[0][0]) > 0 and len(G.den[0][0]) > 0
    # Bode arrays monotonic frequency axis and finite values
    w = np.logspace(-1, 2, 64)
    bode = bode_arrays(G, w, s.delay, delay_method="frd")
    assert np.allclose(bode.w, w)
    assert np.isfinite(bode.mag_db).all()
    assert np.isfinite(bode.phase_deg).all()

def test_delay_method_pade_vs_frd_close_mag():
    s = ogata_7_25()
    G = build_rational_tf(s)
    w = np.logspace(-1, 2, 128)
    frd = bode_arrays(G, w, s.delay, delay_method="frd")
    # For Padé, construct rational delay
    numd, dend = ct.pade(s.delay, 6)
    Gp = G * ct.TransferFunction(numd, dend)
    pade = bode_arrays(Gp, w, s.delay, delay_method="pade")
    # Magnitude should be very similar (< ~0.2 dB typical)
    diff = np.abs(frd.mag_db - pade.mag_db)
    assert np.median(diff) < 0.3

def test_pretty_tf_string():
    s = ogata_7_25()
    G = build_rational_tf(s)
    txt = pretty_tf(G.num[0][0], G.den[0][0])
    assert "TF(num=" in txt and "den=" in txt
