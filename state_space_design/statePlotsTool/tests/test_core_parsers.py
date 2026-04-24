
import numpy as np
import pytest
from state_space_design.statePlotsTool.core import parse_time, parse_vec_real

def test_parse_time_colon_and_list():
    t = parse_time("0:0.5:2")
    assert np.isclose(t[0], 0.0) and np.isclose(t[-1], 2.0) and len(t) == 5
    t2 = parse_time("0, 1, 2")
    assert t2.tolist() == [0.0, 1.0, 2.0]

def test_parse_vec_real_defaults_and_errors():
    v = parse_vec_real(None, 3)
    assert v.tolist() == [1.0, 0.0, 0.0]
    with pytest.raises(ValueError):
        parse_vec_real("1 2", 3)
    with pytest.raises(ValueError):
        parse_vec_real("1 1j", 1)
