
import numpy as np
from stateSpaceDesign.minOrdTfTool.utils import (
    parse_mat, split_tokens_any, parse_cplx_tokens,
    array2str, mat_inline, poly_from_roots, phi_of_A, build_S
)

def test_parse_mat_various_forms():
    assert parse_mat("1 2; 3 4").shape == (2,2)
    assert parse_mat("1, 2; 3, 4").shape == (2,2)
    M = parse_mat("1 0  ;  0 1")
    assert np.allclose(M, np.eye(2))

def test_split_tokens_any_and_parse_cplx_tokens():
    toks = split_tokens_any("-2+2*sqrt(3)j, -2-2*sqrt(3)j, -6")
    vals = parse_cplx_tokens(toks)
    assert len(vals) == 3
    assert np.iscomplexobj(vals)

def test_array2str_and_mat_inline():
    M = np.array([[1.0, 2.0], [3.0, 4.0]])
    s1 = array2str(M, precision=3)
    s2 = mat_inline(M, precision=2)
    assert "[" in s1 and "]" in s1
    assert s2.startswith("[[") and s2.endswith("]]")

def test_poly_phi_buildS():
    Aab = np.array([[1.0, 0.0]])
    Abb = np.array([[0.0, 1.0],[ -2.0, -3.0]])
    roots = np.array([-5.0, -6.0])
    coeff = poly_from_roots(roots)
    P = phi_of_A(Abb, coeff)
    S = build_S(Aab, Abb)
    assert P.shape == Abb.shape
    assert S.shape[0] == Abb.shape[0]
