import os
import numpy as np

# Ensure /mnt/data is importable if running in isolation (CI artifact)
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH","") + (":" if os.environ.get("PYTHONPATH") else "") + "/mnt/data"

from state_space_design.observerGainMatrixTool.utils import parse_matrix, parse_vector, parse_cplx_tokens, parse_cplx_csv, pole_multiplicities, jitter_repeated_poles, pretty_poly

def test_parse_matrix_and_vector():
    A = parse_matrix("0 1; -2 -3")
    v = parse_vector("1, 0")
    assert A.shape == (2,2)
    assert v.shape == (2,1)
    assert float(A[1,0]) == -2.0
    assert float(v[0,0]) == 1.0

def test_complex_parsers_and_poly():
    arr1 = parse_cplx_tokens(["-1+2j", "-1-2j"])
    arr2 = parse_cplx_csv("-1+2j,-1-2j")
    assert arr1.dtype == np.complex128
    assert np.allclose(arr1, arr2)
    coeffs = np.poly(arr1)
    s = pretty_poly(coeffs, var="s")
    assert "s^2" in s

def test_pole_multiplicities_and_jitter():
    poles = np.array([-5,-5,-3], dtype=float)
    mult = pole_multiplicities(poles)
    assert mult.get(-5.0) == 2
    out = jitter_repeated_poles(poles, 1e-3)
    # jitter ensures strictly increasing for repeated clusters
    assert len(set(out)) == 3
