# root_locus_analysis/systemResponseTool/core.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import numpy as np
import control as ct

from .utils import (
    parse_matrix, parse_vector, parse_poly, split_top_level,
    make_logger,
)

log = make_logger(__name__)

# ---------- Data models ----------

@dataclass(slots=True)
class SysStyle:
    name: str
    color: Optional[str] = None
    dash: str = "solid"
    width: float = 3.0


@dataclass(slots=True)
class SysSpec:
    kind: str              # 'tf' or 'ss'
    name: str
    # TF
    num: Optional[np.ndarray] = None
    den: Optional[np.ndarray] = None
    fb: str = "unity"      # 'unity' or 'none'
    # SS
    A: Optional[np.ndarray] = None
    B: Optional[np.ndarray] = None
    C: Optional[np.ndarray] = None
    D: Optional[np.ndarray] = None
    in_idx: int = 0
    out_idx: int = 0
    # IC options (SS)
    x0: Optional[np.ndarray] = None
    outs_sel: Optional[List[int]] = None
    # style
    style: SysStyle = field(default_factory=lambda: SysStyle(name="sys"))


class Responses(str, Enum):
    STEP = "step"
    RAMP = "ramp"
    IMPULSE = "impulse"
    ARB = "arb"
    IC1 = "ic1"
    IC2 = "ic2"


class ICMode(Enum):
    IC1 = 1
    IC2 = 2


# ---------- Parsing ----------

class Parser:
    def parse_sys_arg(self, s: str) -> SysSpec:
        toks = split_top_level(s.strip(), ";")
        if not toks:
            raise ValueError("Empty --sys spec.")
        kind = toks[0].strip().lower()
        if kind not in ("tf", "ss"):
            raise ValueError("First token must be 'tf' or 'ss'.")

        kv = {}
        for tok in toks[1:]:
            if "=" not in tok:
                raise ValueError(f"Bad token in --sys: '{tok}'. Use key=value; separate by ';'")
            k, v = tok.split("=", 1)
            kv[k.strip().lower()] = v.strip()

        name = kv.get("name", kv.get("label", kind.upper()))
        style = SysStyle(
            name=name,
            color=kv.get("color"),
            dash=kv.get("dash", "solid"),
            width=float(kv.get("width", 3.0)),
        )

        if kind == "tf":
            num_s = kv.get("num", "")
            den_s = kv.get("den", "")
            if not num_s or not den_s:
                raise ValueError("TF requires num=..., den=...")
            num = parse_poly(num_s)
            den = parse_poly(den_s)
            fb = kv.get("fb", "unity").lower()
            if fb not in ("unity", "none"):
                raise ValueError("fb must be 'unity' or 'none'")
            log.info("Built system '%s' (tf, fb=%s).", name, fb)
            return SysSpec(kind="tf", name=name, num=num, den=den, fb=fb, style=style)

        # SS
        A = parse_matrix(kv.get("a", kv.get("A", "")))
        B = parse_matrix(kv.get("b", kv.get("B", "")))
        C = parse_matrix(kv.get("c", kv.get("C", "")))
        D = parse_matrix(kv.get("d", kv.get("D", "")))
        if A.size == 0 or B.size == 0 or C.size == 0 or D.size == 0:
            raise ValueError("SS requires A=, B=, C=, D= matrices.")

        in_idx = int(kv.get("in", 0))
        out_idx = int(kv.get("out", 0))
        fb = kv.get("fb", "unity").lower()
        if fb not in ("unity", "none"):
            raise ValueError("fb must be 'unity' or 'none'")

        x0 = parse_vector(kv["x0"]) if "x0" in kv else None

        outs_sel = None
        if "outs" in kv:
            sv = kv["outs"].strip().lower()
            if sv == "all":
                outs_sel = list(range(C.shape[0]))
            else:
                toks2 = [t for t in sv.replace(",", " ").split() if t.strip()]
                outs_sel = sorted(set([int(t) for t in toks2]))

        log.info("Built system '%s' (ss, fb=%s).", name, fb)
        return SysSpec(
            kind="ss", name=name, A=A, B=B, C=C, D=D,
            in_idx=in_idx, out_idx=out_idx, fb=fb,
            x0=x0, outs_sel=outs_sel, style=style
        )


# ---------- TF builder ----------

class TransferFunctionBuilder:
    def tf_for_io(self, spec: SysSpec) -> ct.TransferFunction:
        if spec.kind == "tf":
            G = ct.tf(spec.num, spec.den)
            return ct.feedback(G, 1) if spec.fb == "unity" else G
        sys_ss = ct.ss(spec.A, spec.B, spec.C, spec.D)
        try:
            G_io = ct.ss2tf(sys_ss)[spec.out_idx, spec.in_idx]
        except Exception as e:
            raise ValueError(f"Invalid in/out index for SS: {e}") from e
        return ct.feedback(G_io, 1) if spec.fb == "unity" else G_io


# ---------- signals ----------

class SignalGenerator:
    def ramp(self, T: np.ndarray) -> Tuple[np.ndarray, str]:
        U = T.copy()
        return U, "u(t)=t (ramp)"

    def arb(
        self, kind: str, T: np.ndarray, amp: float, freq: float,
        duty: float, expr: str, file_path: str
    ) -> Tuple[np.ndarray, str]:
        if kind == "ramp":
            return self.ramp(T)
        if kind == "sine":
            return amp * np.sin(2*np.pi*freq*T), f"u(t)={amp:g}·sin(2π{freq:g}t)"
        if kind == "square":
            try:
                from scipy.signal import square
            except Exception as e:
                raise RuntimeError("scipy is required for square input.") from e
            return amp * square(2*np.pi*freq*T, duty), f"u(t)={amp:g}·square(2π{freq:g}t, duty={duty:g})"
        if kind == "expr":
            safe = {"t": T, "pi": np.pi, "sin": np.sin, "cos": np.cos, "exp": np.exp,
                    "sqrt": np.sqrt, "log": np.log, "abs": np.abs}
            try:
                U = eval(expr, {"__builtins__": {}}, safe)
            except Exception as e:
                raise ValueError(f"[arb expr] could not eval '{expr}': {e}") from e
            U = np.asarray(U, dtype=float)
            if U.shape != T.shape:
                raise ValueError(f"[arb expr] expression returned shape {U.shape}, expected {T.shape}")
            return U, f"u(t)={expr}"
        if kind == "file":
            try:
                data = np.genfromtxt(file_path, delimiter=",", dtype=float, names=True)
                if data.size == 0 or ("t" not in data.dtype.names or "u" not in data.dtype.names):
                    data = np.loadtxt(file_path, delimiter=",", ndmin=2)
                    if data.ndim != 2 or data.shape[1] < 2:
                        raise ValueError("CSV must have at least 2 columns: t,u")
                    t_col, u_col = data[:, 0], data[:, 1]
                else:
                    t_col, u_col = np.asarray(data["t"]), np.asarray(data["u"])
            except ValueError as ve:
                raise ValueError(f"[arb file] {ve}") from ve
            except Exception as e:
                raise ValueError(f"[arb file] cannot read '{file_path}': {e}") from e
            # We return raw u(t); caller can interpolate to its own grid if needed.
            return np.asarray(u_col, float), f"u(t) from '{file_path}'"
        raise ValueError(f"Unknown arb kind '{kind}'")


# ---------- engine (wrappers + IC) ----------

class ResponseEngine:
    # Robust unpackers (python-control varies by version)
    def _unpack_step(self, res):
        if isinstance(res, tuple):
            return np.asarray(res[0]), np.asarray(res[1])
        T = getattr(res, "time", getattr(res, "t", None))
        Y = getattr(res, "outputs", getattr(res, "y", None))
        if T is None or Y is None:
            raise RuntimeError("ct.step_response returned unsupported object.")
        return np.asarray(T), np.asarray(Y)

    def _unpack_forced(self, res):
        if isinstance(res, tuple):
            if len(res) == 3:
                T, Y, X = res
                return np.asarray(T), np.asarray(Y), (np.asarray(X) if X is not None else None)
            if len(res) == 2:
                T, Y = res
                return np.asarray(T), np.asarray(Y), None
            raise RuntimeError("ct.forced_response tuple length unexpected.")
        T = getattr(res, "time", getattr(res, "t", None))
        Y = getattr(res, "outputs", getattr(res, "y", None))
        X = getattr(res, "states", getattr(res, "x", None))
        if T is None or Y is None:
            raise RuntimeError("ct.forced_response returned unsupported object.")
        return np.asarray(T), np.asarray(Y), (np.asarray(X) if X is not None else None)

    def step(self, sys, T):
        try:
            res = ct.step_response(sys, T=T)
        except TypeError:
            res = ct.step_response(sys, T)
        return self._unpack_step(res)

    def impulse(self, sys, T):
        try:
            res = ct.impulse_response(sys, T=T)
        except TypeError:
            res = ct.impulse_response(sys, T)
        return self._unpack_step(res)

    def forced(self, sys, U, T):
        try:
            res = ct.forced_response(sys, T=T, U=U)
        except TypeError:
            res = ct.forced_response(sys, T, U)
        return self._unpack_forced(res)

    def step_info_safe(self, sys) -> dict:
        try:
            return ct.step_info(sys)
        except Exception:
            return {"RiseTime": float("nan"), "SettlingTime": float("nan"), "Overshoot": float("nan")}

    # ------ initial-condition modes (Ogata §5-5) ------
    def ic_case1_direct(self, A: np.ndarray, x0: np.ndarray, T: np.ndarray) -> np.ndarray:
        """Case 1: states as outputs (C=I), u ≡ 0."""
        n = A.shape[0]
        sys = ct.ss(A, np.zeros((n, 1)), np.eye(n), np.zeros((n, 1)))
        t, X = ct.initial_response(sys, T=T, X0=x0)
        X = np.asarray(X, float)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        return X

    def ic_case1_step_equiv(self, A: np.ndarray, x0: np.ndarray, T: np.ndarray) -> np.ndarray:
        """
        Step-equivalent for Case 1 (states as outputs):
          System: A, B = A x0, C = I, D = x0, input u(t) = 1
        Produces x(t) = e^{At} x0.
        """
        n = A.shape[0]
        x0 = np.asarray(x0).reshape(n)
        B = (A @ x0).reshape(n, 1)     # A x0
        C = np.eye(n)
        D = x0.reshape(n, 1)           # + x0 term
        sys = ct.ss(A, B, C, D)
        U = np.ones_like(T)
        t, X, _ = self.forced(sys, U, T)
        X = np.asarray(X, float)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        return X

    def ic_case2_direct(self, A: np.ndarray, C_sel: np.ndarray, x0: np.ndarray, T: np.ndarray) -> np.ndarray:
        """Case 2: outputs y = C_sel x from x(0)=x0, u ≡ 0."""
        n = A.shape[0]
        m = C_sel.shape[0]
        sys = ct.ss(A, np.zeros((n, 1)), C_sel, np.zeros((m, 1)))
        t, Y = ct.initial_response(sys, T=T, X0=x0)
        Y = np.asarray(Y, float)
        if Y.ndim == 1:
            Y = Y.reshape(1, -1)
        return Y

    def ic_case2_step_equiv(self, A: np.ndarray, C_sel: np.ndarray, x0: np.ndarray, T: np.ndarray) -> np.ndarray:
        """
        Step-equivalent for Case 2 (selected outputs):
          System: A, B = A x0, C = C_sel, D = C_sel x0, input u(t) = 1
        Produces y(t) = C_sel e^{At} x0.
        """
        n = A.shape[0]
        x0 = np.asarray(x0).reshape(n)
        B = (A @ x0).reshape(n, 1)            # A x0
        D = (C_sel @ x0.reshape(n, 1))        # + C_sel x0
        sys = ct.ss(A, B, C_sel, D)
        U = np.ones_like(T)
        t, Y, _ = self.forced(sys, U, T)
        Y = np.asarray(Y, float)
        if Y.ndim == 1:
            Y = Y.reshape(1, -1)
        return Y
