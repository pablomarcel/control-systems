
from types import SimpleNamespace

def test_build_tf_modes_all():
    import numpy as np
    import control as ct
    import frequency_response.plotTool.design as design

    # A) num/den
    G1 = design.build_tf_from_modes("1, 2", "1, 3, 2", None, None, None, None, None, 1.0)
    print("[design] G1:", G1)

    # B) gain + poles
    G2 = design.build_tf_from_modes(None, None, 10.0, None, "0, -1, -5", None, None, 1.0)
    print("[design] G2:", G2)

    # C) factored fnum/fden + K
    G3 = design.build_tf_from_modes(None, None, None, None, None, "K", "s (s+1)", 2.0)
    print("[design] G3:", G3)

def test_build_L_from_args_three_modes():
    import frequency_response.plotTool.design as design

    ns = lambda **kw: SimpleNamespace(**kw)

    common = dict(scale=None, A=None, B=None, C=None, D=None)

    # factored
    args1 = ns(num=None, den=None, gain=None, zeros=None, poles=None, fnum="K", fden="s (s+1)", K=1.0, **common)
    Ls1, names1 = design.build_L_from_args(args1)
    print("[build_L factored] names:", names1)
    assert len(Ls1) == 1 and names1 == ["y1 from u1"]

    # zpk-like
    args2 = ns(num=None, den=None, gain=10.0, zeros=None, poles="0, -1, -5", fnum=None, fden=None, K=1.0, **common)
    Ls2, names2 = design.build_L_from_args(args2)
    print("[build_L zpk] names:", names2)
    assert len(Ls2) == 1

    # poly lists
    args3 = ns(num="1,2", den="1,3,2", gain=None, zeros=None, poles=None, fnum=None, fden=None, K=1.0, **common)
    Ls3, names3 = design.build_L_from_args(args3)
    print("[build_L poly] names:", names3)
    assert len(Ls3) == 1

def test_build_tf_invalid_combo_raises():
    import frequency_response.plotTool.design as design
    import pytest
    with pytest.raises(ValueError):
        design.build_tf_from_modes(None, None, None, None, None, None, None, 1.0)
