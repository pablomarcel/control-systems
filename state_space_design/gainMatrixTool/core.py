from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Any, Dict, Optional
import numpy as np
import control as ct
from .utils import to_jsonable, pretty_matrix, timed

@dataclass
class GainMatrixRequest:
    mode: str  # "K", "L", or "KI"
    A: np.ndarray
    B: Optional[np.ndarray] = None
    C: Optional[np.ndarray] = None
    poles: Optional[list] = None
    method: str = "auto"
    verify: bool = False
    pretty: bool = False

def parse_matrix(s: str, dtype=float) -> np.ndarray:
    rows = [r.strip() for r in s.strip().split(";") if r.strip()]
    mat = [[float(x.replace("i","j").replace("j","j")) for x in row.replace(",", " ").split()] for row in rows]
    return np.array(mat, dtype=dtype)

def parse_vector(s: str) -> np.ndarray:
    toks = [t for t in s.replace(",", " ").split() if t]
    return np.array([complex(t.replace("i","j")) for t in toks], dtype=complex)

def parse_poles_arg(poles_arg) -> list:
    if isinstance(poles_arg, list) and len(poles_arg) == 1:
        return parse_vector(poles_arg[0]).tolist()
    if isinstance(poles_arg, list) and len(poles_arg) > 1:
        return parse_vector(" ".join(poles_arg)).tolist()
    if isinstance(poles_arg, str):
        return parse_vector(poles_arg).tolist()
    raise ValueError("Unable to parse poles")

def is_controllable(A: np.ndarray, B: np.ndarray) -> Tuple[bool, int]:
    M = ct.ctrb(A, B)
    rank = np.linalg.matrix_rank(M)
    return (rank == A.shape[0], rank)

def is_observable(A: np.ndarray, C: np.ndarray) -> Tuple[bool, int]:
    M = ct.obsv(A, C)
    rank = np.linalg.matrix_rank(M)
    return (rank == A.shape[0], rank)

def almost_controllable_canonical(A: np.ndarray, tol: float = 1e-9) -> bool:
    n = A.shape[0]
    ok = True
    for i in range(n-1):
        if abs(A[i, i+1] - 1.0) > tol:
            ok = False
            break
    S = A.copy()
    for i in range(n-1):
        S[i, :] = 0.0
        S[i, i+1] = 1.0
    return ok and np.allclose(A[:-1,:], S[:-1,:], atol=tol)

def companion_coef_difference_K(A: np.ndarray, B: np.ndarray, poles: list) -> np.ndarray:
    n = A.shape[0]
    charA = np.poly(A)
    a = charA[1:]
    charD = np.poly(np.array(poles, dtype=complex))
    alpha = np.real_if_close(charD[1:])
    diffs = (np.array(alpha, dtype=float) - np.array(a, dtype=float))[::-1]
    K = diffs.reshape(1, -1)
    return K

def choose_method(A: np.ndarray, B: np.ndarray, method: str) -> str:
    if method != "auto":
        return method
    m = B.shape[1] if B.ndim == 2 else 1
    if m == 1 and almost_controllable_canonical(A):
        return "companion"
    return "acker" if m == 1 else "place"

def place_gain(A: np.ndarray, B: np.ndarray, poles: list, method: str) -> np.ndarray:
    m = B.shape[1] if B.ndim == 2 else 1
    if method == "companion":
        return companion_coef_difference_K(A, B, poles)
    if method == "acker":
        K = ct.acker(A, B, poles)
        if np.ndim(K) == 1:
            K = K.reshape(1, -1)
        return np.array(K, dtype=float)
    if method == "place":
        K = ct.place(A, B, poles)
        if np.ndim(K) == 1:
            K = K.reshape(1, -1)
        return np.array(K, dtype=float)
    raise ValueError("Unknown method")

@timed
def verify_poles(M: np.ndarray, desired: list):
    eigs = np.linalg.eigvals(M)
    eigs = np.sort_complex(eigs)
    des  = np.sort_complex(np.array(desired, dtype=complex))
    return eigs, (eigs - des)

@dataclass
class GainMatrixResult:
    payload: dict

class GainMatrixDesigner:
    """Core design engine for state feedback (K), observer (L), and servo (kI)."""

    def _report(self, s: str, pretty: bool):
        if pretty:
            print(s)

    def _result(self, **k) -> GainMatrixResult:
        return GainMatrixResult(payload=k)

    def _verify_out(self, pretty: bool, label: str, Acl: np.ndarray, poles: list, result: dict):
        eigs, diff = verify_poles(Acl, poles)
        if pretty:
            from .utils import pretty_matrix
            print(f"\n== Verification ==\n{label} eigs = {pretty_matrix(eigs)}")
            ok = np.allclose(np.sort_complex(eigs), np.sort_complex(np.array(poles)), atol=1e-6)
            print("Pole match: " + ("OK ✅" if ok else f"NOT EXACT (numeric diff shown)"))
            if not ok:
                print(pretty_matrix(diff))
        result["poles_closed"] = to_jsonable(eigs)

    def design_K(self, A: np.ndarray, B: np.ndarray, poles: list, method: str = "auto", verify: bool = False, pretty: bool = False) -> GainMatrixResult:
        ok, r = is_controllable(A, B)
        self._report(f"\n== Controllability ==\nrank(ctrb(A,B)) = {r} (n = {A.shape[0]}) -> {'CONTROLLABLE ✅' if ok else 'NOT CONTROLLABLE ❌'}", pretty)
        if not ok:
            raise SystemExit("System not controllable; cannot place poles.")
        msel = choose_method(A, B, method)
        self._report(f"\n== Method ==\nSelected: {'companion (coef-difference)' if msel=='companion' else msel}", pretty)
        K = place_gain(A, B, poles, msel)
        if pretty:
            self._report(f"\n== Result ==\nK shape: {K.shape}\nK = {pretty_matrix(K)}", pretty)
        result = {"mode":"K","A":to_jsonable(A),"B":to_jsonable(B),"poles_desired":to_jsonable(poles),"K":to_jsonable(K)}
        if verify:
            Acl = A - B @ K
            self._verify_out(pretty, "eig(A - B K)", Acl, poles, result)
        return self._result(**result)

    def design_L(self, A: np.ndarray, C: np.ndarray, poles: list, method: str = "auto", verify: bool = False, pretty: bool = False) -> GainMatrixResult:
        ok, r = is_observable(A, C)
        self._report(f"\n== Observability ==\nrank(obsv(A,C)) = {r} (n = {A.shape[0]}) -> {'OBSERVABLE ✅' if ok else 'NOT OBSERVABLE ❌'}", pretty)
        if not ok:
            raise SystemExit("System not observable; cannot place observer poles.")
        msel = "acker" if method == "auto" else method
        if msel not in ("acker","place"):
            msel = "acker"
        self._report(f"\n== Method ==\nSelected: {msel}", pretty)
        Lt = place_gain(A.T, C.T, poles, msel)
        L = Lt.T
        if pretty:
            self._report(f"\n== Result ==\nL shape: {L.shape}\nL = {pretty_matrix(L)}", pretty)
        result = {"mode":"L","A":to_jsonable(A),"C":to_jsonable(C),"poles_desired":to_jsonable(poles),"L":to_jsonable(L)}
        if verify:
            Acl = A - L @ C
            self._verify_out(pretty, "eig(A - L C)", Acl, poles, result)
        return self._result(**result)

    def design_KI(self, A: np.ndarray, B: np.ndarray, C: np.ndarray, poles: list, method: str = "auto", verify: bool = False, pretty: bool = False) -> GainMatrixResult:
        n = A.shape[0]
        Ahat = np.block([[A, np.zeros((n,1))], [-C, np.zeros((1,1))]])
        Bhat = np.vstack([B, np.zeros((1, B.shape[1] if B.ndim==2 else 1))])
        ok, r = is_controllable(Ahat, Bhat)
        self._report(f"\n== Augmented controllability (KI) ==\nrank(ctrb(Ahat,Bhat)) = {r} (n+1 = {n+1}) -> {'CONTROLLABLE ✅' if ok else 'NOT CONTROLLABLE ❌'}", pretty)
        if not ok:
            raise SystemExit("Augmented system not controllable; cannot place poles.")
        msel = "acker" if method == "auto" or method == "companion" else method
        self._report(f"\n== Method ==\nSelected: {msel}", pretty)
        Khat = place_gain(Ahat, Bhat, poles, msel)
        K = Khat[0, :n].reshape(1, -1)
        kI = -float(Khat[0, n])
        if pretty:
            self._report(f"\n== Result ==\nK shape: {K.shape},  kI: scalar\nK = {pretty_matrix(K)}\nkI = {kI:.6f}", pretty)
        result = {"mode":"KI","A":to_jsonable(A),"B":to_jsonable(B),"C":to_jsonable(C),"poles_desired":to_jsonable(poles),"K":to_jsonable(K),"kI":float(kI)}
        if verify:
            Acl_hat = Ahat - Bhat @ Khat
            self._verify_out(pretty, "eig(Ahat - Bhat Khat)", Acl_hat, poles, result)
        return self._result(**result)
