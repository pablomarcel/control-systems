from __future__ import annotations

"""Application orchestration for observer gain matrix design."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple

import numpy as np
from numpy.linalg import eigvals
from scipy import signal
from scipy.linalg import expm

from .apis import ObserverRequest, ObserverResponse
from .utils import (
    parse_matrix,
    parse_vector,
    parse_cplx_tokens,
    parse_cplx_csv,
    pretty_poly,
)
from .core import obsv_matrix
from .design import ObserverDesigner, ControllerDesigner
from .io import OutputManager


# ---------------------- LaTeX helpers ----------------------
def latex_bmatrix(M: np.ndarray) -> str:
    """Render a minimal LaTeX bmatrix string without a SymPy dependency."""
    rows = [" ".join([f"{v:g}" for v in row]) for row in M]
    return "\\begin{bmatrix}" + " \\\\ ".join(rows) + "\\end{bmatrix}"


def latex_equation(
    A: np.ndarray, B: Optional[np.ndarray], C: np.ndarray, Ke: np.ndarray
) -> str:
    """Build a display-math LaTeX snippet for the observer equation."""
    Acl = A - Ke @ C
    pieces = [latex_bmatrix(Acl) + "\\,\\tilde{x}"]
    if B is not None:
        pieces.append(latex_bmatrix(B) + "\\,u")
    pieces.append(latex_bmatrix(Ke) + ("\\,\\mathbf{y}" if C.shape[0] > 1 else "\\,y"))
    rhs = " + ".join(pieces)
    header = "\\dot{\\tilde{x}} = (A - K_e C)\\,\\tilde{x}"
    if B is not None:
        header += " + B\\,u"
    header += " + K_e\\," + ("\\mathbf{y}" if C.shape[0] > 1 else "y")
    # Carefully escaped newlines/brackets for Python string literals.
    return ("\\[\\n" + header + "\\\\n= " + rhs + " \\\\n\\]\\n")


# ---------------------- Closed-loop / TF / sim ----------------------
def build_augmented(
    A: np.ndarray, B: np.ndarray, C: np.ndarray, K: np.ndarray, Ke: np.ndarray
) -> np.ndarray:
    """Build the augmented separation-structure state matrix."""
    if A.shape[0] != A.shape[1]:
        raise ValueError("A must be square for augmented build.")
    n = A.shape[0]
    if B.shape[0] != n or C.shape[1] != n:
        raise ValueError("Dimension mismatch in B/C for augmented build.")
    if K.shape[1] != n or Ke.shape[0] != n:
        raise ValueError("Dimension mismatch in K/Ke for augmented build.")

    A_BK = A - B @ K
    A_KeC = A - Ke @ C
    top = np.hstack([A_BK, B @ K])
    bot = np.hstack([np.zeros((n, n)), A_KeC])
    return np.vstack([top, bot])


def observer_controller_tf(
    A: np.ndarray, B: np.ndarray, C: np.ndarray, K: np.ndarray, Ke: np.ndarray
) -> Tuple[list, list]:
    """Compute the observer-controller transfer-function numerator and denominator."""
    # A_c is the closed-loop dynamics seen by the observer-controller path.
    A_c = A - Ke @ C - B @ K
    B_c = Ke
    C_c = K
    D_c = np.zeros((1, B_c.shape[1]))
    num, den = signal.ss2tf(A_c, B_c, C_c, D_c)
    # num is shaped (outputs, inputs, order+1); this tool reports the u-from-y path.
    return num[0].tolist(), den.tolist()


def simulate_initial(
    A_aug: np.ndarray,
    C: np.ndarray,
    K: np.ndarray,
    x0: np.ndarray,
    e0: np.ndarray,
    t_final: float,
    dt: float,
) -> Tuple[list, list, list, list, list]:
    """Simulate the zero-input augmented system by exact discretization."""
    if t_final <= 0:
        raise ValueError("t_final must be positive for simulation.")
    if dt <= 0:
        raise ValueError("dt must be positive for simulation.")
    if x0.ndim != 2 or e0.ndim != 2:
        raise ValueError("x0 and e0 must be column vectors (n×1).")

    z0 = np.vstack([x0.reshape(-1, 1), e0.reshape(-1, 1)])
    Phi = expm(A_aug * dt)
    N = int(np.round(t_final / dt)) + 1
    n = x0.size
    t = np.linspace(0.0, dt * (N - 1), N)
    z = z0.copy()
    X = np.zeros((n, N))
    E = np.zeros((n, N))
    U = np.zeros(N)
    Y = np.zeros(N)
    for k in range(N):
        x = z[:n, :]
        e = z[n:, :]
        X[:, k] = x[:, 0]
        E[:, k] = e[:, 0]
        U[k] = float((-(K @ (x - e)))[0, 0])
        Y[k] = float(((C @ x))[0, 0])
        z = Phi @ z
    return t.tolist(), X.tolist(), E.tolist(), U.tolist(), Y.tolist()


# ---------------------- Application ----------------------
@dataclass
class ObserverGainMatrixApp:
    """Orchestrate observer gain design and optional reporting outputs."""

    out: OutputManager = field(default_factory=OutputManager)

    def _parse_and_validate(self, req: ObserverRequest) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
        """Parse request matrices and validate their dimensions."""
        A = parse_matrix(req.A)
        C = parse_matrix(req.C)
        if A.ndim != 2 or A.shape[0] != A.shape[1]:
            raise ValueError("A must be a square 2D matrix.")
        if C.ndim != 2 or C.shape[1] != A.shape[0]:
            raise ValueError("C must be 2D with n columns matching A.")
        B = parse_matrix(req.B) if req.B else None
        if B is not None and (B.ndim != 2 or B.shape[0] != A.shape[0]):
            raise ValueError("B must be 2D with n rows matching A.")
        return A, B, C

    def _design_observer(self, A: np.ndarray, C: np.ndarray, req: ObserverRequest) -> Tuple[np.ndarray, Dict[str, Any], str]:
        """Compute the observer gain matrix and metadata."""
        n = A.shape[0]
        if not isinstance(req.poles, (list, tuple, np.ndarray)):
            raise ValueError("poles must be a sequence of complex (or real) values.")
        if len(req.poles) != n:
            raise ValueError(f"Observer poles must have length n={n}.")

        # Observability check.
        Mo = obsv_matrix(A, C)
        if np.linalg.matrix_rank(Mo) != n:
            raise ValueError("System not observable (rank(Mo) < n).")

        designer = ObserverDesigner()
        poles_e = np.array(req.poles, dtype=complex)
        res = designer.compute(
            A, C, poles_e, method=req.method, place_fallback=req.place_fallback, jitter_eps=req.jitter_eps
        )
        Ke = np.asarray(res.Ke).reshape(n, C.shape[0])
        meta = {
            "method_used": res.method_used,
            "place_fallback_used": res.meta.get("place_fallback_used"),
            "poles_used_for_place": res.meta.get("poles_used_for_place"),
        }
        return Ke, meta, res.method_used

    def _design_controller_if_requested(
        self, A: np.ndarray, B: Optional[np.ndarray], C: np.ndarray, req: ObserverRequest
    ) -> Optional[np.ndarray]:
        """Compute an optional state-feedback gain from explicit values or poles."""
        n = A.shape[0]
        if req.K:
            K = parse_matrix(req.K).reshape(1, -1)
            if K.shape[1] != n:
                raise ValueError(f"Provided K must have length n={n}.")
            return K

        # Poles form: CSV or list.
        poles_tokens = None
        if req.K_poles_list:
            poles_tokens = req.K_poles_list
        elif req.K_poles_csv:
            poles_tokens = [req.K_poles_csv]

        if not poles_tokens:
            return None

        if B is None:
            raise ValueError("B is required if K poles provided.")

        poles_k = parse_cplx_tokens(poles_tokens) if req.K_poles_list else parse_cplx_csv(req.K_poles_csv)  # type: ignore[arg-type]
        if poles_k.size != n:
            raise ValueError(f"K_poles length must be n={n}.")
        return ControllerDesigner().compute_place(A, B, poles_k)

    def _pretty_block(self, A: np.ndarray, C: np.ndarray, Ke: np.ndarray, method_used: str, meta: Dict[str, Any]) -> list[str]:
        """Build human-friendly summary strings."""
        Aerr = A - Ke @ C
        # Stable characteristic polynomial coefficients, real part only.
        char_ach = np.poly(np.sort_complex(eigvals(Aerr))).real
        blocks = [
            "== Full-Order Observer Design ==",
            f"Used method: {method_used}  |  place_fallback: {meta.get('place_fallback_used')}",
        ]
        if method_used == "place" and meta.get("place_fallback_used") == "jitter":
            blocks.append(f"Poles used for place(): {meta.get('poles_used_for_place')}")
        blocks.append(f"Ke (n×p):\n{Ke}")
        blocks.append(f"|sI - (A - Ke C)| = {pretty_poly(char_ach)}")
        return blocks

    def run(self, req: ObserverRequest) -> ObserverResponse:
        """Run the full observer-gain workflow and return structured results."""
        # Parse and validate.
        A, B, C = self._parse_and_validate(req)
        n = A.shape[0]

        # Observer gain.
        Ke, meta, method_used = self._design_observer(A, C, req)

        # Optional controller gain.
        K = self._design_controller_if_requested(A, B, C, req)

        # Pretty strings.
        pretty_blocks: list[str] = []
        if req.pretty:
            pretty_blocks = self._pretty_block(A, C, Ke, method_used, meta)

        # Optional LaTeX.
        latex_path: Optional[str] = None
        if req.latex_out:
            latex_text = latex_equation(A, B, C, Ke)
            latex_path = str(self.out.write_text(latex_text, req.latex_out))

        # Closed-loop model, transfer function, and simulation.
        A_BK = A_KeC = A_aug = None
        tf_num = tf_den = None
        sim = None
        if req.compute_closed_loop:
            if K is None or Ke is None or B is None:
                raise ValueError("compute_closed_loop requires both K and K_e (and B).")
            A_BK = A - B @ K
            A_KeC = A - Ke @ C
            A_aug = build_augmented(A, B, C, K, Ke)
            tf_num, tf_den = observer_controller_tf(A, B, C, K, Ke)
            if req.x0 and req.e0 and req.t_final > 0:
                x0 = parse_vector(req.x0)
                e0 = parse_vector(req.e0)
                if x0.size != n or e0.size != n:
                    raise ValueError(f"x0 and e0 must each have length n={n}.")
                t, X, E, U, Y = simulate_initial(A_aug, C, K, x0, e0, req.t_final, req.dt)
                sim = {"t": t, "x": X, "e": E, "u": U, "y": Y}

        data: Dict[str, Any] = {
            "A": A.tolist(),
            "B": (B.tolist() if B is not None else None),
            "C": C.tolist(),
            "Ke": Ke.tolist(),
            "K": (K.tolist() if K is not None else None),
            "observer": meta,
            "A_minus_KeC": (A - Ke @ C).tolist(),
            "A_minus_BK": (A_BK.tolist() if A_BK is not None else None),
            "A_augmented": (A_aug.tolist() if A_aug is not None else None),
            "observer_controller_tf": ({"num": tf_num, "den": tf_den} if tf_num is not None else None),
            "simulation": sim,
            "latex_path": latex_path,
        }
        return ObserverResponse(data=data, pretty_blocks=pretty_blocks)
