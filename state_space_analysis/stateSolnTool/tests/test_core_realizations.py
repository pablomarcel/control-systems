
from state_space_analysis.stateSolnTool.core import RealizationFactory

def test_controllable_and_observable():
    num_desc = [1,3]
    den_desc = [1,3,2]
    R = RealizationFactory.controllable(num_desc, den_desc)
    assert R.A.shape[0] == R.B.shape[0] == 2
    Ro = RealizationFactory.observable(R.A).A
    assert Ro.shape == R.A.shape

def test_diagonal_and_jordan():
    # Simple poles -> diagonal exists
    den_desc = [1,3,2]  # (s+1)(s+2)
    Rd = RealizationFactory.diagonal(den_desc)
    assert Rd is not None and Rd.A.shape[0] == 2
    # Repeated poles -> diagonal returns None
    den_rep = [1,2,1]  # (s+1)^2
    assert RealizationFactory.diagonal(den_rep) is None
    # Jordan from controllable
    Rc = RealizationFactory.controllable([1,3],[1,3,2])
    Rj = RealizationFactory.jordan(Rc.A, Rc.B)
    assert Rj.A.shape == Rc.A.shape
