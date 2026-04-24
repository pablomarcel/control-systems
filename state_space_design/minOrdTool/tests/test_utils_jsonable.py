
import numpy as np
from state_space_design.minOrdTool.utils import to_jsonable, array2str, mat_inline, pretty_poly

def test_to_jsonable_covers_arrays_complex_and_nested():
    data = {
        "A": np.array([[1,2],[3,4]], float),
        "z": 1+0j,
        "w": 2+3j,
        "v": np.array([1+0j, 2+5j]),
        "nested": [{"x": np.complex64(0+0j)}]
    }
    js = to_jsonable(data)
    assert isinstance(js["A"], list)
    assert js["z"] == 1.0
    assert js["w"] == [2.0, 3.0]
    assert isinstance(js["v"], list) and isinstance(js["v"][0], (float, int))

def test_array2str_and_mat_inline_and_pretty_poly():
    A = np.array([[0,1],[ -2,-3 ]], float)
    s = array2str(A, precision=3)
    t = mat_inline(A, precision=2)
    p = pretty_poly([1, 3, 2], var="s")
    assert "[[" in t and "]]" in t
    assert "s^2" in p and "3s" in p and "+ 2" in p
