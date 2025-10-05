
import numpy as np
from stateSpaceDesign.minOrdTool.io import parse_mat, parse_poles_tokens, _split_list_any

def test_parse_mat_basic_and_complex():
    M = parse_mat("1 2; 3 4")
    assert M.shape == (2,2)
    Mc = parse_mat("1 2i; -3j 4")
    assert Mc.shape == (2,2)
    assert np.iscomplexobj(Mc)

def test_parse_poles_tokens_variants():
    toks = ["-1", "-2+2*sqrt(3)j", "-2-2*sqrt(3)j"]
    arr = parse_poles_tokens(toks)
    assert arr.shape == (3,)
    assert any(np.iscomplex(o) for o in arr)

def test_split_list_any():
    s = "-1, -2 -3,  -4"
    out = _split_list_any(s)
    assert out == ["-1","-2","-3","-4"]
