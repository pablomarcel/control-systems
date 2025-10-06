
import numpy as np
import pytest
from stateSpaceDesign.observerStatePlotTool.utils import parse_time, parse_vec_real, to2d, safe_series, ensure_out_path

def test_parse_time_variants():
    t1 = parse_time("0:0.5:1.0")
    assert np.allclose(t1, [0.0, 0.5, 1.0])
    t2 = parse_time("0, 1, 2")
    assert np.allclose(t2, [0.0, 1.0, 2.0])

def test_parse_vec_real_defaults_and_errors():
    v = parse_vec_real(None, 3, default_first_one=True)
    assert np.allclose(v, [1.0, 0.0, 0.0])
    v2 = parse_vec_real("0, 2, 3", 3, default_first_one=False)
    assert np.allclose(v2, [0.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        parse_vec_real("1 2", 3)  # wrong length
    with pytest.raises(ValueError):
        parse_vec_real("1 (1+2j) 3", 3)  # complex remains

def test_to2d_and_safe_series_and_paths(tmp_path):
    a = np.array([1,2,3])
    a2 = to2d(a)
    assert a2.shape == (1,3)
    b = safe_series("b", [1, 2.5, 3])
    assert b.dtype.kind in ("i","f")
    out = ensure_out_path("tmp.csv", "fallback.csv")
    assert out.endswith("stateSpaceDesign/observerStatePlotTool/out/tmp.csv")
