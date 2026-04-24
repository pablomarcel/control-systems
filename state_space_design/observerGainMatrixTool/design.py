from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np
from numpy.linalg import inv, matrix_rank
from .core import ctrb_dual, phi_of_matrix, ctrb_matrix
from .utils import pole_multiplicities, jitter_repeated_poles

# Optional deps (soft)
try:
    import control as ct
    HAS_CTRL = True
except Exception:
    HAS_CTRL = False

@dataclass
class ObserverDesignResult:
    Ke: np.ndarray
    method_used: str
    meta: Dict[str, Any]

class ObserverDesigner:
    """Compute full-order observer gains K_e using 'place' (dual) or Ackermann."""

    def method_ackermann_dual(self, A: np.ndarray, C: np.ndarray, poles: np.ndarray) -> np.ndarray:
        if C.shape[0] != 1:
            raise ValueError("Ackermann requires SISO output (C is 1×n).")
        n = A.shape[0]
        Cd = ctrb_dual(A, C)
        if matrix_rank(Cd) != n:
            raise ValueError("Dual not controllable (rank(Cd) < n) ⇒ not observable.")
        r = np.zeros((1, n)); r[0, -1] = 1.0
        Ke = (r @ inv(Cd) @ phi_of_matrix(A.T, poles)).T
        return np.real_if_close(Ke)

    def method_place_dual(self, A: np.ndarray, C: np.ndarray, poles: np.ndarray,
                          place_fallback: str = "none", jitter_eps: float = 1e-6
                          ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if not HAS_CTRL:
            raise RuntimeError("Install `control` to use place().")
        meta = {"place_fallback_used": "none", "poles_used_for_place": np.real_if_close(poles).tolist()}
        p = C.shape[0]
        mult = pole_multiplicities(poles)
        max_mult = max(mult.values()) if mult else 1
        if max_mult > p:
            msg = (f"Requested repeated pole multiplicity {max_mult} exceeds p=rank(C^T)={p} "
                   "(dual place restriction).")
            if place_fallback == "ack" and p == 1:
                Ke = self.method_ackermann_dual(A, C, poles); meta["place_fallback_used"] = "ack"
                return Ke, meta
            if place_fallback == "jitter":
                poles = jitter_repeated_poles(poles, jitter_eps)
                meta["place_fallback_used"] = "jitter"
                meta["poles_used_for_place"] = poles.tolist()
            else:
                raise ValueError(msg + " Try place_fallback=jitter or method='ack' for SISO.")
        Ke = ct.place(A.T, C.T, poles).T
        return np.real_if_close(Ke), meta

    def compute(self, A: np.ndarray, C: np.ndarray, poles: np.ndarray,
                method: str = "auto", place_fallback: str = "none", jitter_eps: float = 1e-6
                ) -> ObserverDesignResult:
        method = method.lower()
        meta = {"place_fallback_used":"none","poles_used_for_place":None}
        if method == "place":
            Ke, meta2 = self.method_place_dual(A, C, poles, place_fallback, jitter_eps)
            meta.update(meta2); used = "place"
        elif method == "ack":
            Ke = self.method_ackermann_dual(A, C, poles); used = "ack"
        else:
            # auto
            try:
                Ke, meta2 = self.method_place_dual(A, C, poles, "none", jitter_eps)
                meta.update(meta2); used = "place"
            except Exception:
                if C.shape[0] == 1:
                    Ke = self.method_ackermann_dual(A, C, poles); used = "ack"
                else:
                    raise
        return ObserverDesignResult(Ke=Ke, method_used=used, meta=meta)

class ControllerDesigner:
    """State-feedback K via place() if available, else SISO Ackermann fallback."""

    def compute_place(self, A: np.ndarray, B: np.ndarray, poles: np.ndarray) -> np.ndarray:
        try:
            import control as ct  # local import for clarity
            return np.real_if_close(ct.place(A, B, poles))
        except Exception:
            # SISO Ackermann fallback
            if B.shape[1] != 1:
                raise RuntimeError("python-control missing and m>1; cannot do multiinput Ackermann.")
            from .core import phi_of_matrix, ctrb_matrix
            n = A.shape[0]
            Mc = ctrb_matrix(A, B)
            if matrix_rank(Mc) != n:
                raise ValueError("Not controllable: rank(Mc) < n.")
            r = np.zeros((1, n)); r[0, -1] = 1.0
            return np.real_if_close(r @ np.linalg.inv(Mc) @ phi_of_matrix(A, poles))
