import numpy as np
from state_space_design.servoTool.utils import parse_matrix, parse_time, ensure_2d_row, ensure_col, default_state_names, default_output_names
from state_space_design.servoTool.core import ServoIOModel, ServoMode
from state_space_design.servoTool.tools import plotting

def test_utils_parsers_and_shapes():
    M = parse_matrix("1, 2; 3, 4")
    assert M.shape == (2,2) and M[0,1] == 2
    T = parse_time("0:0.5:1.5")
    assert T.tolist() == [0.0,0.5,1.0,1.5]
    T2 = parse_time("0, 1, 2")
    assert T2.tolist() == [0.0,1.0,2.0]
    assert ensure_2d_row([1,2]).shape == (1,2)
    assert ensure_col([1,2]).shape == (2,1)
    assert default_state_names(3) == ["x1","x2","x3"]
    assert default_output_names(2) == ["y1","y2"]

def test_core_to_jsonable_flags_and_tools_import():
    model = ServoIOModel(
        mode=ServoMode.K,
        Acl=np.eye(1),
        Bcl=np.ones((1,1)),
        C=np.ones((1,1)),
        D=np.zeros((1,1)),
        r=1.0,
        k_r=2.0,
        kI=None,
        state_names=["x1"],
        output_names=["y1"],
    )
    payload = model.to_jsonable()
    assert payload["k_r"] == 2.0
    # Touch tools.plotting
    assert plotting is not None
