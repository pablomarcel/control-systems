import numpy as np
from transient_analysis.icTool.tfcore import TfProblem, TfSolver

def test_tfcore_num_ic_path():
    pb = TfProblem(den=np.array([1.0,3.0,2.0]), num_ic=np.array([0.1,0.05,0.0]))
    T = np.linspace(0, 0.1, 6)
    T2, Y = TfSolver(pb).step_equiv_output(T)
    assert T2.shape == T.shape and Y.shape[1] == T.shape[0]

def test_tfcore_mbk_path():
    pb = TfProblem(den=np.array([1.0,3.0,2.0]), m=1.0,b=3.0,k=2.0,x0=0.1,v0=0.05)
    T = np.linspace(0, 0.1, 6)
    T2, Y = TfSolver(pb).step_equiv_output(T)
    assert T2.shape == T.shape and Y.shape[1] == T.shape[0]