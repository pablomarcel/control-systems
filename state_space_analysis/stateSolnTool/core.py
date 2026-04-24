
# core.py — state-solution engine (OOP)
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterable, Optional
import numpy as np
import sympy as sp

from .utils import sym_s, sym_t, pretty_matrix, to_expr_t, is_square_free
from .io import parse_tf_string, parse_poly, normalize_monic, ensure_proper, coeffs_asc, parse_vec_csv

# ----------- Realization building -------------------------------------------

@dataclass
class Realization:
    A: sp.Matrix
    B: sp.Matrix

class RealizationFactory:
    @staticmethod
    def controllable(num_desc, den_desc) -> Realization:
        a_desc = den_desc
        n = len(a_desc) - 1
        if n <= 0:
            raise ValueError("Denominator must be at least first order.")
        a_asc = coeffs_asc(a_desc[1:], n)
        A = sp.zeros(n)
        for i in range(n-1):
            A[i, i+1] = 1
        A[n-1, :] = sp.Matrix([[-ai for ai in a_asc]])
        B = sp.zeros(n, 1); B[n-1, 0] = 1
        return Realization(A, B)

    @staticmethod
    def observable(Ac: sp.Matrix) -> Realization:
        n = Ac.shape[0]
        Ao = Ac.T
        Bo = sp.zeros(n, 1); Bo[0,0] = 1
        return Realization(Ao, Bo)

    @staticmethod
    def diagonal(den_desc) -> Optional[Realization]:
        s = sym_s()
        D = sp.Poly(den_desc, s)
        if not is_square_free(D):
            return None
        roots = list(sp.roots(D.as_expr()).keys())
        def sort_key(z): return (float(sp.re(z).evalf()), float(sp.im(z).evalf()))
        poles = sorted((sp.nsimplify(r) for r in roots), key=sort_key, reverse=True)
        A = sp.diag(*poles)
        B = sp.ones(len(poles), 1)
        return Realization(A, B)

    @staticmethod
    def jordan(A: sp.Matrix, B: sp.Matrix) -> Realization:
        P, J = A.jordan_form()
        Pinv = P.inv()
        Bj = Pinv * B
        return Realization(J, Bj)

# ----------- Solver & Verifier ----------------------------------------------

class StateSolver:
    def __init__(self, realization: Realization, t0: float = 0.0):
        self.A = realization.A
        self.B = realization.B
        self.t0 = float(t0)

    @staticmethod
    def phi(A: sp.Matrix, t: sp.Symbol) -> sp.Matrix:
        return (A*t).exp()

    def solve(self, u_expr: sp.Expr, x0: sp.Matrix) -> Tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
        t = sym_t()
        Phi = self.phi(self.A, t - self.t0)
        x_hom = Phi * x0
        tau = sp.Symbol('tau', real=True)
        integrand = Phi.subs(t, t - tau) * self.B * u_expr.subs(t, tau)
        x_part = sp.integrate(integrand, (tau, self.t0, t))
        x_t = sp.simplify(x_hom + x_part)
        return Phi, x_hom, x_part, x_t

class SolutionVerifier:
    @staticmethod
    def _simplify_matrix(M: sp.Matrix) -> sp.Matrix:
        return M.applyfunc(lambda e: sp.simplify(sp.together(e)))

    @staticmethod
    def _is_zero_symbolic(M: sp.Matrix) -> bool:
        Ms = SolutionVerifier._simplify_matrix(M)
        return all(Ms[i, j] == 0 for i in range(Ms.rows) for j in range(Ms.cols))

    @staticmethod
    def _max_abs_numeric(M: sp.Matrix) -> float:
        return max(float(abs(complex(sp.N(M[i, j])))) for i in range(M.rows) for j in range(M.cols))

    @staticmethod
    def _numeric_zero_over_samples(exprM: sp.Matrix, t: sp.Symbol, samples: Iterable[float], tol: float) -> bool:
        for tv in samples:
            Mv = exprM.subs(t, tv)
            if SolutionVerifier._max_abs_numeric(Mv) > tol:
                return False
        return True

    @staticmethod
    def verify(A: sp.Matrix, B: sp.Matrix, u_expr: sp.Expr, x0: sp.Matrix,
               x_t: sp.Matrix, t0: float, tol: float = 1e-9) -> Tuple[bool, str]:
        t = sym_t()
        xdot = x_t.diff(t)
        res = SolutionVerifier._simplify_matrix(xdot - (A * x_t + B * u_expr))
        if SolutionVerifier._is_zero_symbolic(res):
            ode_ok = True
            ode_msg = "ODE residual is identically zero (symbolic)."
        else:
            samples = [t0, t0 + 0.1, t0 + 0.5, t0 + 1.0]
            ode_ok = SolutionVerifier._numeric_zero_over_samples(res, t, samples, tol)
            ode_msg = ("ODE residual small on samples (numeric fallback)." if ode_ok
                       else f"ODE residual not zero; max|res| at samples > {tol}.")

        ic_res = SolutionVerifier._simplify_matrix(x_t.subs(t, t0) - x0)
        if SolutionVerifier._is_zero_symbolic(ic_res):
            ic_ok = True
            ic_msg = "Initial condition holds exactly (symbolic)."
        else:
            ic_ok = SolutionVerifier._max_abs_numeric(ic_res) <= tol
            ic_msg = ("Initial condition holds numerically." if ic_ok
                      else f"Initial condition mismatch; ||x(t0)-x0||∞ > {tol}.")

        ok = ode_ok and ic_ok
        msg = f"{'PASS' if ok else 'FAIL'} — {ode_msg} {ic_msg}"
        return ok, msg

# ----------- Facade / Orchestration -----------------------------------------

class StateSolnEngine:
    EXAMPLES = {
        "ogata_9_1": "(s+3)/(s**2+3*s+2)"
    }

    def __init__(self, canonical: str = "controllable"):
        self.canonical = canonical

    def _build_realization(self, num_desc, den_desc) -> Realization:
        Rc = RealizationFactory.controllable(num_desc, den_desc)
        if self.canonical == "controllable":
            return Rc
        if self.canonical == "observable":
            return RealizationFactory.observable(Rc.A)
        if self.canonical == "diagonal":
            Rm = RealizationFactory.diagonal(den_desc)
            return Rm if Rm is not None else Rc
        if self.canonical == "jordan":
            return RealizationFactory.jordan(Rc.A, Rc.B)
        raise ValueError("Unknown canonical form.")

    def parse_tf(self, tf: str | None, num: str | None, den: str | None, example: str | None):
        if example:
            tf = self.EXAMPLES.get(example)
        if tf:
            num_desc, den_desc = parse_tf_string(tf)
        else:
            if not (num and den):
                raise ValueError("Provide tf OR both num and den.")
            num_desc = parse_poly(num)
            den_desc = parse_poly(den)
        num_desc, den_desc = normalize_monic(num_desc, den_desc)
        num_desc, den_desc, _ = ensure_proper(num_desc, den_desc)
        return num_desc, den_desc

    def run(self, *, tf=None, num=None, den=None, example=None, u="1", x0=None,
            t0=0.0, eval_time=None, numeric=False, digits=8, pretty=False,
            verify=False, tol=1e-9, export_json: Optional[str] = None):
        # Parse TF
        num_desc, den_desc = self.parse_tf(tf, num, den, example)
        # Realization
        R = self._build_realization(num_desc, den_desc)
        n = R.A.shape[0]
        # Initial condition
        x0_vec = parse_vec_csv(x0, n) if x0 else sp.zeros(n, 1)
        # Input
        u_expr = to_expr_t(u)
        # Solve
        solver = StateSolver(R, t0=t0)
        Phi, x_hom, x_part, x_t = solver.solve(u_expr, x0_vec)

        # Prepare presentation
        if eval_time is not None:
            tv = float(eval_time)
            A_txt = str(sp.Matrix(R.A))
            B_txt = str(sp.Matrix(R.B))
            Phi_txt = str(sp.Matrix(Phi.subs(sym_t(), tv)))
            xh_txt  = str(sp.Matrix(x_hom.subs(sym_t(), tv)))
            xp_txt  = str(sp.Matrix(x_part.subs(sym_t(), tv)))
            x_txt   = str(sp.Matrix(x_t.subs(sym_t(), tv)))
        else:
            format_fun = pretty_matrix if pretty else (lambda M: str(sp.Matrix(M)))
            A_txt = str(sp.Matrix(R.A))
            B_txt = str(sp.Matrix(R.B))
            Phi_txt = format_fun(Phi)
            xh_txt  = format_fun(x_hom)
            xp_txt  = format_fun(x_part)
            x_txt   = format_fun(x_t)

        # Verify
        ver_msg = None
        if verify:
            ok, msg = SolutionVerifier.verify(R.A, R.B, u_expr, x0_vec, x_t, float(t0), tol=tol)
            ver_msg = msg

        # Optional export
        if export_json:
            payload = {
                "A": [[str(sp.nsimplify(R.A[i, j])) for j in range(R.A.shape[1])] for i in range(R.A.shape[0])],
                "B": [[str(sp.nsimplify(R.B[i, j])) for j in range(R.B.shape[1])] for i in range(R.B.shape[0])],
                "Phi(t)": [[str(sp.simplify(Phi[i, j])) for j in range(Phi.shape[1])] for i in range(Phi.shape[0])],
                "x_hom(t)": [[str(sp.simplify(x_hom[i, 0]))] for i in range(x_hom.shape[0])],
                "x_part(t)": [[str(sp.simplify(x_part[i, 0]))] for i in range(x_part.shape[0])],
                "x(t)": [[str(sp.simplify(x_t[i, 0]))] for i in range(x_t.shape[0])]
            }
            from .io import save_json
            save_json(export_json, payload)

        return {
            "A": A_txt,
            "B": B_txt,
            "Phi": Phi_txt,
            "x_hom": xh_txt,
            "x_part": xp_txt,
            "x": x_txt,
            "verification": ver_msg
        }
