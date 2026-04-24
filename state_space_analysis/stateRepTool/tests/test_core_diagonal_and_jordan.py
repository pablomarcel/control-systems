
from state_space_analysis.stateRepTool.core import TransferFunctionSpec, CanonicalFormCalculator

def test_diagonal_pf_simple_poles():
    spec = TransferFunctionSpec.from_tf_string("(s+3)/(s^2+3*s+2)")
    calc = CanonicalFormCalculator(tf=spec, verify=True)
    reals = calc.compute(which="all")
    assert "diagonal" in reals
    diag = reals["diagonal"]
    assert diag.A.shape == (2,2) and diag.B.shape == (2,1) and diag.C.shape == (1,2)

def test_repeated_poles_jordan_present_and_diagonal_optional():
    # Repeated pole system: 1/(s+1)^2 -> not diagonalizable (Jordan blocks). Our calculator may
    # skip 'diagonal' if eigen diagonalization fails, but must include 'jordan'.
    spec = TransferFunctionSpec.from_tf_string("1/(s+1)^2")
    calc = CanonicalFormCalculator(tf=spec, verify=True)
    reals = calc.compute(which="all")
    assert "jordan" in reals
    # 'diagonal' may be absent for defective matrices; if present, check dimensions.
    if "diagonal" in reals:
        dj = reals["diagonal"]
        assert dj.A.shape == (2,2)
