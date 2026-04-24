from state_space_design.gainMatrixTool.utils import timed

@timed
def f():
    return 42

def test_timed_decorator_returns_value():
    assert f() == 42
