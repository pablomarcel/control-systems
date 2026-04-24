from __future__ import annotations
import numpy as np
import control as ct
from typing import Optional
from .core import ControllerPayload, ServoMode, ServoIOModel
from .utils import default_state_names, default_output_names, ensure_2d_row

class ServoSynthesizer:
    """Implements K- and KI-mode servo I/O synthesis."""

    def __init__(self, payload: ControllerPayload, C_override: Optional[np.ndarray] = None):
        self.payload = payload
        self.C_override = C_override

    def build(self, r: float = 1.0, k_r_override: Optional[float] = None) -> ServoIOModel:
        if self.payload.mode == ServoMode.K:
            return self._build_k_mode(r=r, k_r_override=k_r_override)
        elif self.payload.mode == ServoMode.KI:
            return self._build_ki_mode(r=r)
        else:
            raise ValueError("Unsupported mode for ServoSynthesizer (use K or KI).")

    # -------- K mode --------
    def _build_k_mode(self, r: float, k_r_override: Optional[float]) -> ServoIOModel:
        A = np.array(self.payload.A, dtype=float)
        B = np.array(self.payload.B, dtype=float)
        K = np.array(self.payload.K, dtype=float) if self.payload.K is not None else None
        if K is None:
            raise ValueError("K mode requires K in controller payload")
        K = ensure_2d_row(K)

        # choose C: override > payload > error
        if self.C_override is not None:
            C = np.array(self.C_override, dtype=float)
        elif self.payload.C is not None:
            C = np.array(self.payload.C, dtype=float)
        else:
            raise ValueError("For mode=K, C is required (not found in JSON; provide --C).")
        C = ensure_2d_row(C)

        Acl = A - B @ K

        if k_r_override is not None:
            k_r = float(k_r_override)
        else:
            X = np.linalg.inv(Acl) @ B
            denom = (C @ X).item()
            if abs(denom) < 1e-12:
                raise ValueError("Cannot compute k_r: C (A-BK)^{-1} B ≈ 0.")
            k_r = -1.0 / denom

        n = A.shape[0]
        p = C.shape[0]
        state_names = self.payload.state_names or default_state_names(n)
        output_names = self.payload.output_names or default_output_names(p)

        Aio = Acl
        Bio = B * k_r
        Cio = C
        Dio = np.zeros((p, 1))

        return ServoIOModel(
            mode=ServoMode.K,
            Acl=Aio, Bcl=Bio, C=Cio, D=Dio,
            r=float(r), k_r=float(k_r),
            state_names=state_names,
            output_names=output_names,
        )

    # -------- KI mode --------
    def _build_ki_mode(self, r: float) -> ServoIOModel:
        A = np.array(self.payload.A, dtype=float)
        B = np.array(self.payload.B, dtype=float)
        C = np.array(self.payload.C, dtype=float) if self.payload.C is not None else None
        if C is None:
            raise ValueError("KI mode requires C in controller payload")
        C = ensure_2d_row(C)

        K = np.array(self.payload.K, dtype=float) if self.payload.K is not None else None
        if K is None:
            raise ValueError("KI mode requires K in controller payload")
        K = ensure_2d_row(K)

        if self.payload.kI is None:
            raise ValueError("KI mode requires kI in controller payload")
        kI = float(self.payload.kI)

        n = A.shape[0]
        p = C.shape[0]
        state_names = (self.payload.state_names or default_state_names(n)) + ["xi"]
        output_names = self.payload.output_names or default_output_names(p)

        Acl = A - B @ K
        Aio = np.block([[Acl,        B * kI],
                        [-C,         np.zeros((p,1))]])
        Bio = np.vstack([np.zeros((n,1)), np.ones((1,1))])
        Cio = np.hstack([C, np.zeros((p,1))])
        Dio = np.zeros((p,1))

        return ServoIOModel(
            mode=ServoMode.KI,
            Acl=Aio, Bcl=Bio, C=Cio, D=Dio,
            r=float(r), kI=float(kI),
            state_names=state_names,
            output_names=output_names,
        )

    # -------- quick step (preview only) --------
    @staticmethod
    def quick_step(model: ServoIOModel, T):
        sysio = ct.ss(model.Acl, model.Bcl, model.C, model.D)
        T, Y = ct.step_response(sysio, T=T)
        if Y.ndim > 1:
            Y = Y[0, :]
        return T, model.r * Y
