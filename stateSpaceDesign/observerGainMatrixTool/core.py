from __future__ import annotations
import numpy as np
from numpy.linalg import matrix_rank

def obsv_matrix(A: np.ndarray, C: np.ndarray) -> np.ndarray:
    n = A.shape[0]
    blocks = [C]
    Ap = np.eye(n)
    for _ in range(1, n):
        Ap = Ap @ A
        blocks.append(C @ Ap)
    return np.vstack(blocks)

def ctrb_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    n = A.shape[0]
    cols = [B]
    Ap = np.eye(n)
    for _ in range(1, n):
        Ap = Ap @ A
        cols.append(Ap @ B)
    return np.column_stack(cols)

def ctrb_dual(A: np.ndarray, C: np.ndarray) -> np.ndarray:
    n = A.shape[0]
    cols = [C.T]
    ApT = A.T.copy()
    for _ in range(1, n):
        cols.append(ApT @ C.T)
        ApT = ApT @ A.T
    return np.column_stack(cols)

def phi_coeffs_from_poles(poles: np.ndarray) -> np.ndarray:
    return np.real_if_close(np.poly(poles))

def phi_of_matrix(A: np.ndarray, poles: np.ndarray) -> np.ndarray:
    coeffs = phi_coeffs_from_poles(poles)
    n = A.shape[0]
    M = np.zeros_like(A, dtype=float)
    for a in coeffs:
        M = M @ A + a * np.eye(n)
    return M

def is_observable(A: np.ndarray, C: np.ndarray) -> bool:
    from numpy.linalg import matrix_rank
    return matrix_rank(obsv_matrix(A, C)) == A.shape[0]
