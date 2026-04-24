
import sympy as sp
from state_space_analysis.stateSolnTool.core import StateSolnEngine, StateSolver, SolutionVerifier
from state_space_analysis.stateSolnTool.utils import sym_t, to_expr_t

def test_solve_shapes_and_ic():
    eng = StateSolnEngine(canonical="controllable")
    num_desc, den_desc = eng.parse_tf(None, "1,3", "1,3,2", None)
    R = eng._build_realization(num_desc, den_desc)
    solver = StateSolver(R, t0=0.0)
    t = sym_t()
    Phi, xh, xp, xt = solver.solve(to_expr_t("1"), sp.zeros(R.A.shape[0], 1))
    assert Phi.shape[0] == Phi.shape[1] == R.A.shape[0]
    # Check IC: x(0) = 0
    assert xt.subs(t, 0) == sp.zeros(R.A.shape[0], 1)

def test_verifier_numeric_fallback():
    eng = StateSolnEngine(canonical="controllable")
    res = eng.run(example="ogata_9_1", u="exp(-t)", verify=True, tol=1e-10)
    assert "PASS" in (res["verification"] or "")
