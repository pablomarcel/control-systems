from __future__ import annotations
import numpy as np
import control as ct
import types
import importlib

from stateSpaceAnalysis.converterTool.utils import (
    parse_vector, parse_matrix, normalize_tf, clip_small, coeffs_from_tf, coerce_outputs_to_m_by_N
)

def test_parse_vector_and_matrix_and_normalize():
    v = parse_vector("1, 0, 2")
    assert v.tolist() == [1.0, 0.0, 2.0]
    M = parse_matrix("1 2; 3 4")
    assert M.shape == (2,2)
    num = np.array([0, 1.0])
    den = np.array([0, 2.0, 2.0])
    n2, d2 = normalize_tf(num, den)
    # leading coefficient of den becomes 1
    assert d2[0] == 1.0
    assert np.isclose(n2[-1], 0.5)

def test_clip_small_and_coeffs_from_tf():
    arr = np.array([1e-14, 1.0, -1e-15])
    out = clip_small(arr, tol=1e-12)
    assert out[0] == 0.0 and out[-1] == 0.0 and out[1] == 1.0
    G = ct.TransferFunction([1, 0], [1, 1])
    n, d = coeffs_from_tf(G)
    assert d[0] == 1.0 and n.shape[0] == d.shape[0]

def test_coerce_outputs_to_m_by_N_shapes():
    N = 5
    # 1-D -> (1, N)
    y = np.arange(N)
    Y = coerce_outputs_to_m_by_N(y, N_time=N)
    assert Y.shape == (1, N)
    # (m, N) untouched
    y2 = np.vstack([np.arange(N), np.arange(N)])
    Y2 = coerce_outputs_to_m_by_N(y2, N_time=N)
    assert Y2.shape == (2, N)
    # (N, m) -> transpose
    y3 = np.vstack([np.arange(N), np.arange(N)]).T
    Y3 = coerce_outputs_to_m_by_N(y3, N_time=N)
    assert Y3.shape == (2, N)
    # (m,1,N) -> collapse
    y4 = np.arange(2*1*N).reshape(2,1,N)
    Y4 = coerce_outputs_to_m_by_N(y4, N_time=N)
    assert Y4.shape == (2, N)
