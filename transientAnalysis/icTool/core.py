# ---------------------------------
# File: transientAnalysis/icTool/core.py
# ---------------------------------
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .utils import (
    _to_2d,
    _ensure_1d,
    safe_ss,
    initial_response_safe,
    forced_response_safe,
    CaseResult,
    CompareResult,
    track,
)

@dataclass(slots=True)
class ICProblem:
    """Problem data for response to initial conditions.

    Parameters
    ----------
    A : ndarray (n,n)
        State matrix.
    x0 : ndarray (n,)
        Initial state.
    C : ndarray (m,n), optional
        Output map for Case 2. For Case 1, C is ignored and I is used.
    """
    A: np.ndarray
    x0: np.ndarray
    C: np.ndarray | None = None

    def __post_init__(self) -> None:
        self.A = np.asarray(self.A, dtype=float)
        self.x0 = _ensure_1d(self.x0)
        if self.A.shape[0] != self.A.shape[1]:
            raise ValueError("A must be square")
        n = self.A.shape[0]
        if self.x0.size != n:
            raise ValueError(f"x0 length {self.x0.size} != A.shape[0] {n}")
        if self.C is not None:
            self.C = np.asarray(self.C, dtype=float)
            if self.C.shape[1] != n:
                raise ValueError("C must have n columns")


class ICSolver:
    """Compute responses to initial conditions (Case 1 and Case 2).

    Shapes: all outputs are normalized to (rows, N) arrays.
    """
    def __init__(self, pb: ICProblem) -> None:
        self.pb = pb

    # ----- Case 1: states x(t) with C = I ----- #
    @track("ICSolver.case1_direct", "control.initial_response")
    def case1_direct(self, T: np.ndarray) -> CaseResult:
        A, x0 = self.pb.A, self.pb.x0
        n = A.shape[0]
        I = np.eye(n)
        sys_direct = safe_ss(A, np.zeros((n, 1)), I, np.zeros((n, 1)))
        Td, Xd = initial_response_safe(sys_direct, T=T, X0=x0)
        labels = tuple(f"x{i+1}" for i in range(n))
        return CaseResult(T=Td, Y=Xd, label_rows=labels)

    @track("ICSolver.case1_step_equiv", "control.forced_response")
    def case1_step_equiv(self, T: np.ndarray) -> CaseResult:
        """Step-equivalent model that reproduces **states** x(t).

        Use ż = A z + x0·u(t) with z(0)=0 and choose the output as
            y = A z + x0·u(t)  (i.e., C=A, D=x0)
        so that y(t) = ż(t) = x(t) for a unit-step u(t).
        """
        A, x0 = self.pb.A, self.pb.x0
        n = A.shape[0]
        B_step = x0.reshape(n, 1)
        C_step = A
        D_step = x0.reshape(n, 1)
        sys_step = safe_ss(A, B_step, C_step, D_step)
        U = np.ones_like(T)
        Ts, Ys = forced_response_safe(sys_step, T=T, U=U)
        labels = tuple(f"x{i+1}" for i in range(n))
        return CaseResult(T=Ts, Y=Ys, label_rows=labels)

    def compare1(self, T: np.ndarray) -> CompareResult:
        return CompareResult(direct=self.case1_direct(T), step_equiv=self.case1_step_equiv(T))

    # ----- Case 2: outputs y(t) = C x(t) ----- #
    @track("ICSolver.case2_direct", "control.initial_response")
    def case2_direct(self, T: np.ndarray) -> CaseResult:
        A, x0 = self.pb.A, self.pb.x0
        C = self.pb.C if self.pb.C is not None else np.eye(A.shape[0])
        n, m = A.shape[0], C.shape[0]
        sys_direct = safe_ss(A, np.zeros((n, 1)), C, np.zeros((m, 1)))
        Td, Yd = initial_response_safe(sys_direct, T=T, X0=x0)
        labels = tuple(f"y{i+1}" for i in range(m))
        return CaseResult(T=Td, Y=Yd, label_rows=labels)

    @track("ICSolver.case2_step_equiv", "control.forced_response")
    def case2_step_equiv(self, T: np.ndarray) -> CaseResult:
        """Step-equivalent model that reproduces **outputs** y(t)=C x(t).

        With ż = A z + x0·u(t), z(0)=0, choose output
            y = C(A z + x0·u(t))  (i.e., C_step = C A, D_step = C x0)
        so that y(t) = C ż(t) = C x(t) for unit-step u(t).
        """
        A, x0 = self.pb.A, self.pb.x0
        C = self.pb.C if self.pb.C is not None else np.eye(A.shape[0])
        n, m = A.shape[0], C.shape[0]
        B_step = x0.reshape(n, 1)
        C_step = C @ A
        D_step = (C @ x0.reshape(n, 1))
        sys_step = safe_ss(A, B_step, C_step, D_step)
        U = np.ones_like(T)
        Ts, Ys = forced_response_safe(sys_step, T=T, U=U)
        labels = tuple(f"y{i+1}" for i in range(m))
        return CaseResult(T=Ts, Y=Ys, label_rows=labels)

    def compare2(self, T: np.ndarray) -> CompareResult:
        return CompareResult(direct=self.case2_direct(T), step_equiv=self.case2_step_equiv(T))