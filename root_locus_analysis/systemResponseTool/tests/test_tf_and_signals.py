
from __future__ import annotations

import numpy as np
import control as ct

from root_locus_analysis.systemResponseTool.core import SysSpec, TransferFunctionBuilder, SignalGenerator

def test_tf_builder_tf_and_ss():
    b = TransferFunctionBuilder()

    # direct TF, no feedback
    spec1 = SysSpec(kind="tf", name="G", num=np.array([1.0]), den=np.array([1.0,1.0]), fb="none")
    G1 = b.tf_for_io(spec1)
    assert isinstance(G1, ct.TransferFunction)

    # SS channel with unity feedback
    A = np.array([[-1.0]])
    B = np.array([[1.0]])
    C = np.array([[1.0]])
    D = np.array([[0.0]])
    spec2 = SysSpec(kind="ss", name="P", A=A,B=B,C=C,D=D, fb="unity", in_idx=0, out_idx=0)
    G2 = b.tf_for_io(spec2)
    assert isinstance(G2, ct.TransferFunction)

def test_signal_generator_ramp_and_expr():
    sg = SignalGenerator()
    T = np.linspace(0, 0.2, 5)
    U, label = sg.ramp(T)
    assert label.startswith("u(t)=t")
    assert np.allclose(U, T)

    Ue, lbl = sg.arb("expr", T, 1.0, 1.0, 0.5, "sin(2*pi*1*t)", "")
    assert Ue.shape == T.shape
