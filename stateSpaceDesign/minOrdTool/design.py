from __future__ import annotations
import logging
import numpy as np
from .core import SystemSpec, MinOrderObserverDesigner, poly_from_roots
from .utils import array2str, pretty_poly, mat_inline, sympy_pretty_observer

try:
    import control as ct
    HAS_CTRL = True
except Exception:
    HAS_CTRL = False

class MinOrdAppService:
    def __init__(self, precision: int = 4, verbose: bool = False):
        self.precision = precision
        logging.getLogger().setLevel(logging.DEBUG if verbose else logging.INFO)

    def design_observer(self, A, C, poles, B=None, allow_pinv=False, pretty=False, K=None, K_poles=None):
        sys = SystemSpec(A=A, C=C, B=B)
        designer = MinOrderObserverDesigner(sys)
        res = designer.design(poles=np.asarray(poles, dtype=complex), allow_pinv=allow_pinv)

        # Optional state feedback K
        K_row = None
        if K is not None:
            K_row = np.atleast_2d(np.asarray(K, float))
            if K_row.shape != (1, sys.n):
                raise ValueError(f"--K must be 1×{sys.n}.")
        elif K_poles is not None:
            if not HAS_CTRL:
                raise RuntimeError("python-control is required for --K_poles.")
            if sys.B is None or (sys.B.ndim == 2 and sys.B.shape[1] != 1):
                raise ValueError("--K_poles supports SISO B (n×1).")
            kp = np.asarray(K_poles, dtype=complex)
            if len(kp) != sys.n:
                raise ValueError(f"--K_poles needs n={sys.n} poles.")
            K_row = np.real_if_close(ct.acker(sys.A, sys.B, kp), 1e8).astype(float)

        # Diagnostics
        eig_obs = np.linalg.eigvals(res["Ahat"])
        coeff_obs = poly_from_roots(eig_obs)
        desired_coeff = poly_from_roots(np.asarray(poles, dtype=complex))
        match = np.allclose(coeff_obs, desired_coeff, rtol=1e-7, atol=1e-8)

        # Pretty printing
        if pretty:
            print("\n== Minimum-Order Observer (Ogata) ==")
            print(f"n = {sys.n},  p = 1  → observer order r = n-1 = {sys.n-1}")
            print(f"C (1×{sys.n}):", array2str(sys.C, self.precision))
            print("T  (rows: C; Null(C)):\n", array2str(res["T"], self.precision))
            print("T⁻¹:\n", array2str(res["Tinv"], self.precision))

            print("\nPartitions in x̄ = [x_a; x_b]:")
            print("  A_aa:", array2str(np.array([[res['Aaa']]]), self.precision))
            print("  A_ab:", array2str(res["Aab"], self.precision))
            print("  A_ba:\n", array2str(res["Aba"], self.precision))
            print("  A_bb:\n", array2str(res["Abb"], self.precision))
            if sys.B is not None:
                Abar, Bbar = res["Abar"], res["Bbar"]
                Ba = Bbar[0:1, :]
                Bb = Bbar[1:, :]
                print("  B_a:", array2str(Ba, self.precision))
                print("  B_b:\n", array2str(Bb, self.precision))

            print("\nK_e (column):\n", array2str(res["Ke"], self.precision))
            print("Ahat = A_bb - K_e A_ab:\n", array2str(res["Ahat"], self.precision))
            print("Bhat = Ahat K_e + A_ba - K_e A_aa:\n", array2str(res["Bhat"], self.precision))
            if res["Fhat"] is not None:
                print("Fhat = B_b - K_e B_a:\n", array2str(res["Fhat"], self.precision))

            num1 = "eta_hat_dot = " + " + ".join(filter(None, [
                f"{mat_inline(res['Ahat'], self.precision)}·η̃",
                f"{mat_inline(res['Bhat'], self.precision)}·y",
                (f"{mat_inline(res['Fhat'], self.precision)}·u" if res['Fhat'] is not None else "")
            ]))
            num2 = f"x_hat = {mat_inline(res['Ctil'], self.precision)}·η̃ + {mat_inline(res['Dtil'], self.precision)}·y"
            print("\nOne-line observer equations (numeric):")
            print(num1); print(num2)

            m_inputs = None if res["Fhat"] is None else res["Fhat"].shape[1]
            sympy_pretty_observer(res["Ahat"], res["Bhat"], res["Fhat"], res["Ctil"], res["Dtil"], m_inputs)

            if K_row is not None:
                print("\nControl law with minimum-order observer: u = -K x_hat")
                print("K:", array2str(K_row, self.precision))

            print("\nObserver Ahat eigenvalues:", array2str(np.real_if_close(eig_obs,1e8), self.precision))
            print("Char poly of Ahat (achieved):", pretty_poly(coeff_obs))
            print("Characteristic polynomial match:", "✅" if match else "❌")

        payload = {
            **res,
            "eig_Ahat": np.asarray(eig_obs).tolist(),
            "charpoly_Ahat": np.asarray(coeff_obs, float).tolist(),
            "charpoly_desired": np.asarray(desired_coeff, float).tolist(),
            "charpoly_match": bool(match),
        }
        if K_row is not None:
            payload["K"] = np.asarray(K_row, float).tolist()
        return payload
