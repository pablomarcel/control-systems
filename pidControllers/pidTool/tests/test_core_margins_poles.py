import control as ct
from pidControllers.pidTool.core import margins_report, poles_stable

def test_margins_report_and_poles():
    s = ct.TransferFunction.s
    Gp = 1/(s+1)
    C = 2*(s+0.5)**2/s
    L = C*Gp
    rep = margins_report(L)
    assert isinstance(rep, str) and "Gain margin" in rep
    T = ct.feedback(L, 1)
    # Some control versions return numpy.bool_ here; coerce to bool
    assert bool(poles_stable(T)) is True
