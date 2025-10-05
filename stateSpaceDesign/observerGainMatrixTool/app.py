from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np
from numpy.linalg import eigvals
from scipy import signal
from scipy.linalg import expm

from .apis import ObserverRequest, ObserverResponse
from .utils import parse_matrix, parse_vector, parse_cplx_tokens, parse_cplx_csv, pretty_poly
from .core import obsv_matrix
from .design import ObserverDesigner, ControllerDesigner
from .io import OutputManager

def latex_bmatrix(M: np.ndarray) -> str:
    rows = [" ".join([f"{v:g}" for v in row]) for row in M]
    return "\\begin{bmatrix}" + " \\ ".join(rows) + "\\end{bmatrix}"

def latex_equation(A: np.ndarray, B: Optional[np.ndarray], C: np.ndarray, Ke: np.ndarray) -> str:
    Acl = A - Ke @ C
    pieces = [latex_bmatrix(Acl) + "\\,\\tilde{x}"]
    if B is not None: pieces.append(latex_bmatrix(B) + "\\,u")
    pieces.append(latex_bmatrix(Ke) + ("\\,\\mathbf{y}" if C.shape[0] > 1 else "\\,y"))
    rhs = " + ".join(pieces)
    header = "\\dot{\\tilde{x}} = (A - K_e C)\\,\\tilde{x}"
    if B is not None: header += " + B\\,u"
    header += " + K_e\\," + ("\\mathbf{y}" if C.shape[0] > 1 else "y")
    return "\[\n" + header + "\\\n= " + rhs + " \\\n\]\n"

def build_augmented(A: np.ndarray, B: np.ndarray, C: np.ndarray, K: np.ndarray, Ke: np.ndarray) -> np.ndarray:
    A_BK  = A - B @ K
    A_KeC = A - Ke @ C
    n = A.shape[0]
    top = np.hstack([A_BK,  B @ K])
    bot = np.hstack([np.zeros((n, n)), A_KeC])
    return np.vstack([top, bot])

def observer_controller_tf(A: np.ndarray, B: np.ndarray, C: np.ndarray, K: np.ndarray, Ke: np.ndarray):
    A_c = A - Ke @ C - B @ K
    B_c = Ke
    C_c = K
    D_c = np.zeros((1, B_c.shape[1]))
    num, den = signal.ss2tf(A_c, B_c, C_c, D_c)
    return num[0].tolist(), den.tolist()

def simulate_initial(A_aug: np.ndarray, C: np.ndarray, K: np.ndarray,
                     x0: np.ndarray, e0: np.ndarray,
                     t_final: float, dt: float):
    z0 = np.vstack([x0.reshape(-1,1), e0.reshape(-1,1)])
    Phi = expm(A_aug * dt)
    N = int(np.round(t_final / dt)) + 1
    n = x0.size
    t = np.linspace(0.0, dt*(N-1), N)
    z = z0.copy()
    X = np.zeros((n, N)); E = np.zeros((n, N))
    U = np.zeros(N); Y = np.zeros(N)
    for k in range(N):
        x = z[:n, :]
        e = z[n:, :]
        X[:, k] = x[:, 0]
        E[:, k] = e[:, 0]
        U[k] = float((-(K @ (x - e)))[0, 0])
        Y[k] = float(((C @ x))[0, 0])
        z = Phi @ z
    return t.tolist(), X.tolist(), E.tolist(), U.tolist(), Y.tolist()

@dataclass
class ObserverGainMatrixApp:
    out: OutputManager = OutputManager()

    def run(self, req: ObserverRequest) -> ObserverResponse:
        # Parse matrices
        A = parse_matrix(req.A)
        C = parse_matrix(req.C)
        if A.shape[0] != A.shape[1]:
            raise ValueError("A must be square.")
        if C.shape[1] != A.shape[0]:
            raise ValueError("C must have n columns.")
        B = parse_matrix(req.B) if req.B else None
        n = A.shape[0]

        # Observer design
        if len(req.poles) != n:
            raise ValueError(f"Observer poles must have length n={n}.")
        Mo = obsv_matrix(A, C)
        if np.linalg.matrix_rank(Mo) != n:
            raise ValueError("System not observable (rank(Mo) < n).")
        designer = ObserverDesigner()
        res = designer.compute(A, C, np.array(req.poles, dtype=complex),
                               method=req.method, place_fallback=req.place_fallback,
                               jitter_eps=req.jitter_eps)
        Ke = np.asarray(res.Ke).reshape(n, C.shape[0])

        # Optional controller K
        K = None
        if req.K:
            K = parse_matrix(req.K).reshape(1, -1)
            if K.shape[1] != n:
                raise ValueError(f"Provided K must have length n={n}.")
        else:
            poles_tokens = None
            if req.K_poles_list: poles_tokens = req.K_poles_list
            elif req.K_poles_csv: poles_tokens = [req.K_poles_csv]
            if poles_tokens and B is None:
                raise ValueError("B is required if K poles provided.")
            if poles_tokens and B is not None:
                if req.K_poles_list:
                    poles_k = parse_cplx_tokens(poles_tokens)
                else:
                    poles_k = parse_cplx_csv(req.K_poles_csv)
                if poles_k.size != n:
                    raise ValueError(f"K_poles length must be n={n}.")
                K = ControllerDesigner().compute_place(A, B, poles_k)

        # Pretty block (optional)
        pretty_blocks = []
        if req.pretty:
            Aerr = A - Ke @ C
            char_ach = np.poly(np.sort_complex(eigvals(Aerr))).real
            pretty_blocks.append("== Full-Order Observer Design ==")
            pretty_blocks.append(f"Used method: {res.method_used}  |  place_fallback: {res.meta.get('place_fallback_used')}")
            if res.method_used == "place" and res.meta.get("place_fallback_used") == "jitter":
                pretty_blocks.append(f"Poles used for place(): {res.meta.get('poles_used_for_place')}")
            pretty_blocks.append(f"Ke (n×p):\n{Ke}")
            pretty_blocks.append(f"|sI - (A - Ke C)| = {pretty_poly(char_ach)}")

        # Optional LaTeX
        latex_path = None
        if req.latex_out:
            latex_text = latex_equation(A, B, C, Ke)
            latex_path = self.out.write_text(latex_text, req.latex_out)

        # Closed-loop / TF / sim
        A_BK = A_KeC = A_aug = None
        tf_num = tf_den = None
        sim = None
        if req.compute_closed_loop:
            if K is None or Ke is None or B is None:
                raise ValueError("compute_closed_loop requires both K and K_e (and B).")
            A_BK  = (A - B @ K)
            A_KeC = (A - Ke @ C)
            A_aug = build_augmented(A, B, C, K, Ke)
            tf_num, tf_den = observer_controller_tf(A, B, C, K, Ke)
            if req.x0 and req.e0 and req.t_final > 0:
                x0 = parse_vector(req.x0); e0 = parse_vector(req.e0)
                if x0.size != n or e0.size != n:
                    raise ValueError(f"x0 and e0 must each have length n={n}.")
                t, X, E, U, Y = simulate_initial(A_aug, C, K, x0, e0, req.t_final, req.dt)
                sim = {"t": t, "x": X, "e": E, "u": U, "y": Y}

        data: Dict[str, Any] = {
            "A": A.tolist(),
            "B": (B.tolist() if B is not None else None),
            "C": C.tolist(),
            "Ke": Ke.tolist(),
            "K":  (K.tolist() if K is not None else None),
            "observer": {
                "method_used": res.method_used,
                "place_fallback_used": res.meta.get("place_fallback_used"),
                "poles_used_for_place": res.meta.get("poles_used_for_place"),
            },
            "A_minus_KeC": (A - Ke @ C).tolist(),
            "A_minus_BK": (A_BK.tolist() if A_BK is not None else None),
            "A_augmented": (A_aug.tolist() if A_aug is not None else None),
            "observer_controller_tf": ({"num": tf_num, "den": tf_den} if tf_num is not None else None),
            "simulation": sim,
            "latex_path": (str(latex_path) if latex_path else None),
        }
        return ObserverResponse(data=data, pretty_blocks=pretty_blocks)
