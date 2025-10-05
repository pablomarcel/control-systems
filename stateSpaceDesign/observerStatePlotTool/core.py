from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from .utils import to2d, safe_series, parse_time, parse_vec_real

@dataclass
class SimulationBundle:
    t: np.ndarray
    X: Optional[np.ndarray]
    E: Optional[np.ndarray]
    u: Optional[np.ndarray]
    y: Optional[np.ndarray]

class ObserverStateProcessor:
    def reconstruct_u_y_if_missing(self, payload: Dict[str, Any], t: np.ndarray,
                                   X: Optional[np.ndarray],
                                   E: Optional[np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        u = safe_series("simulation.u", payload.get("simulation", {}).get("u", None))
        y = safe_series("simulation.y", payload.get("simulation", {}).get("y", None))
        if u is None and ("K" in payload) and (X is not None) and (E is not None):
            K = np.asarray(payload["K"], float)
            if K.ndim == 1:
                K = K.reshape(1, -1)
            XE = X - E
            u = (-K @ XE).reshape(-1)  # (N,)
        if y is None and ("C" in payload) and (X is not None):
            C = np.asarray(payload["C"], float)
            yv = (C @ X).reshape(-1, X.shape[1])  # (p,N)
            if yv.shape[0] == 1:
                y = yv[0, :]
            else:
                y = yv  # p×N for MIMO
        return (u, y)

    def simulate_if_missing(self, payload: Dict[str, Any], T: np.ndarray,
                            x0: np.ndarray, e0: np.ndarray) -> SimulationBundle:
        if "A_augmented" not in payload:
            raise ValueError("JSON has no 'simulation' and no 'A_augmented' to simulate.")
        A_aug = np.asarray(payload["A_augmented"], float)
        n2 = A_aug.shape[0]
        if n2 % 2 != 0:
            raise ValueError("A_augmented must have even dimension (2n×2n).")
        n = n2 // 2
        if x0.size != n or e0.size != n:
            raise ValueError(f"x0,e0 must each have length n={n}.")

        # Prefer SciPy expm; otherwise raise a clear message
        try:
            from scipy.linalg import expm
        except Exception as e:
            raise RuntimeError("simulate_if_missing requires SciPy (scipy.linalg.expm).") from e

        dt = float(T[1] - T[0]) if len(T) > 1 else 0.01
        Phi = expm(A_aug * dt)

        z = np.hstack([x0, e0]).reshape(-1, 1)  # (2n,1)
        N = len(T)
        X = np.zeros((n, N))
        E = np.zeros((n, N))
        for k in range(N):
            X[:, k] = z[:n, 0]
            E[:, k] = z[n:, 0]
            z = Phi @ z

        u, y = self.reconstruct_u_y_if_missing(payload, T, X, E)
        if u is None:
            u = np.zeros(N, float)
        if y is None:
            y = np.zeros(N, float)

        return SimulationBundle(T, X, E, u, y)

    def load_or_simulate(self, payload: Dict[str, Any], simulate: bool,
                         t_spec: str, x0_spec: Optional[str], e0_spec: Optional[str]) -> SimulationBundle:
        sim = payload.get("simulation", None)
        if sim is not None and not simulate:
            T = np.asarray(sim.get("t", []), float)
            if T.size == 0:
                raise ValueError("simulation.t is empty.")
            X = to2d(np.asarray(sim.get("x", []), float)) if sim.get("x", None) is not None else None
            E = to2d(np.asarray(sim.get("e", []), float)) if sim.get("e", None) is not None else None
            u = safe_series("simulation.u", sim.get("u", None))
            y = safe_series("simulation.y", sim.get("y", None))
            if y is not None:
                y = np.asarray(y, float)
                if y.ndim == 2 and y.shape[0] == 1:
                    y = y[0, :]
            if (u is None) or (y is None):
                uu, yy = self.reconstruct_u_y_if_missing(payload, T, X, E)
                if u is None:
                    u = uu
                if y is None:
                    y = yy
            return SimulationBundle(T, X, E, u, y)
        # Else simulate (requires A_augmented)
        T = parse_time(t_spec)
        if "A_augmented" not in payload:
            raise ValueError("No 'simulation' in JSON and 'A_augmented' missing. Nothing to plot.")
        n = int(np.asarray(payload["A_augmented"], float).shape[0] // 2)
        x0 = parse_vec_real(x0_spec, n, default_first_one=True)
        e0 = parse_vec_real(e0_spec, n, default_first_one=False)
        return self.simulate_if_missing(payload, T, x0, e0)

    def choose_series(self, want: List[str], X, E, y, u) -> tuple[list[str], list[np.ndarray]]:
        def have(name: str) -> bool:
            return {"x": X is not None, "e": E is not None,
                    "err": (X is not None and E is not None),
                    "y": y is not None, "u": u is not None}[name]

        labels: List[str] = []
        series: List[np.ndarray] = []

        def append_block(prefix: str, M):
            if M is None:
                return
            M2 = to2d(M)  # (n,N)
            for i in range(M2.shape[0]):
                labels.append(f"{prefix}{i+1}")
                series.append(M2[i, :])

        if "x" in want and have("x"):
            append_block("x", X)
        if "e" in want and have("e"):
            append_block("e", E)
        if "err" in want and have("err"):
            append_block("x-e", X - E)
        if "y" in want and have("y"):
            Y = np.asarray(y)
            if Y.ndim == 1:
                labels.append("y")
                series.append(Y.reshape(-1))
            else:
                Y2 = to2d(Y)
                for i in range(Y2.shape[0]):
                    labels.append(f"y{i+1}")
                    series.append(Y2[i, :])
        if "u" in want and have("u"):
            labels.append("u")
            series.append(np.asarray(u).reshape(-1))

        if not series:
            raise ValueError("nothing selected to plot (check 'what').")

        return labels, series
