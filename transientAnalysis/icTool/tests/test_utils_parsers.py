import numpy as np
import pytest
import control as ct

from transientAnalysis.icTool.utils import (
    parse_vector, parse_matrix, parse_poly, time_grid,
    _to_2d, safe_ss, initial_response_safe, forced_response_safe
)

def test_parse_vector_and_poly():
    v = parse_vector("1, 2; 3")
    assert v.tolist() == [1.0, 2.0, 3.0]
    p = parse_poly("[1 3 2]")
    assert p.tolist() == [1.0, 3.0, 2.0]

def test_parse_matrix_and_errors():
    M = parse_matrix("[0 1; -6 -5]")
    assert M.shape == (2,2)
    with pytest.raises(ValueError):
        parse_matrix("[]")
    with pytest.raises(ValueError):
        parse_vector("")

def test_time_grid_errors():
    with pytest.raises(ValueError):
        time_grid(-1, 0.01)
    with pytest.raises(ValueError):
        time_grid(1.0, 0.0)

def test_to2d_and_ss_wrappers():
    a = _to_2d([1,2,3])
    assert a.shape == (1,3)
    A = np.array([[0,1],[-2,-3]], float)
    B = np.zeros((2,1))
    C = np.eye(2)
    D = np.zeros((2,1))
    sys = safe_ss(A,B,C,D)
    T = np.linspace(0, 0.1, 6)
    T0, Y0 = initial_response_safe(sys, T, X0=np.array([0.1, 0.0]))
    assert T0.shape == T.shape and Y0.shape[1] == T.shape[0]
    T1, Y1 = forced_response_safe(sys, T, U=np.ones_like(T))
    assert T1.shape == T.shape and Y1.shape[1] == T.shape[0]