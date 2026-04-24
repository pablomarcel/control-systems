
from __future__ import annotations
import numpy as np
import control as ct
from control_systems.converterTool.design import pretty_tf_any, ConverterPretty, plot_step_tf, plot_step_ss

def test_pretty_and_sympy_if_available():
    G = ct.TransferFunction([1,0], [1,14,56,160])
    txt = pretty_tf_any(G)
    assert "Transfer function" in txt
    sym = ConverterPretty.sympy_rat(G)
    # sympy string may be empty if sympy unavailable, but function must return a str
    assert isinstance(sym, str)

def test_plot_helpers_run_without_gui():
    G = ct.TransferFunction([1,0], [1,14,56,160])
    plot_step_tf(G, tfinal=0.1, dt=0.05, title="smoke tf")
    # Build a tiny SS MIMO and ensure SS plotting path executes
    A = np.array([[-1.0, 0.0],[0.0,-2.0]])
    B = np.array([[1.0,0.0],[0.0,1.0]])
    C = np.eye(2)
    D = np.zeros((2,2))
    ssys = ct.ss(A,B,C,D)
    plot_step_ss(ssys, iu=0, tfinal=0.1, dt=0.05, title="smoke ss")
