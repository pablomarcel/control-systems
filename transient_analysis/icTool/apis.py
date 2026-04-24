# ---------------------------------
# File: transient_analysis/icTool/apis.py
# ---------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import numpy as np

from .core import ICProblem, ICSolver
from .utils import time_grid
from .tfcore import TfProblem, TfSolver  # type: ignore[import]


@dataclass(slots=True)
class ApiResponse:
    ok: bool
    data: Dict[str, Any]
    msg: str = ""


# ================================
# State-space oriented programmatic
# ================================

def compare1_api(A: np.ndarray, x0: np.ndarray, *, tfinal: float, dt: float) -> ApiResponse:
    T = time_grid(tfinal, dt)
    res = ICSolver(ICProblem(A=A, x0=x0)).compare1(T)
    return ApiResponse(ok=True, data={"compare": {
        "direct": res.direct.to_dict(),
        "step_equiv": res.step_equiv.to_dict(),
    }})


def compare2_api(A: np.ndarray, C: np.ndarray, x0: np.ndarray, *, tfinal: float, dt: float) -> ApiResponse:
    T = time_grid(tfinal, dt)
    res = ICSolver(ICProblem(A=A, x0=x0, C=C)).compare2(T)
    return ApiResponse(ok=True, data={"compare": {
        "direct": res.direct.to_dict(),
        "step_equiv": res.step_equiv.to_dict(),
    }})


def case1_api(A: np.ndarray, x0: np.ndarray, *, tfinal: float, dt: float) -> ApiResponse:
    T = time_grid(tfinal, dt)
    res = ICSolver(ICProblem(A=A, x0=x0)).case1_direct(T)
    return ApiResponse(ok=True, data={"case1": res.to_dict()})


def case2_api(A: np.ndarray, C: np.ndarray, x0: np.ndarray, *, tfinal: float, dt: float) -> ApiResponse:
    T = time_grid(tfinal, dt)
    res = ICSolver(ICProblem(A=A, x0=x0, C=C)).case2_direct(T)
    return ApiResponse(ok=True, data={"case2": res.to_dict()})


# ================================
# Transfer-function oriented (Ogata)
# ================================

def tf_step_api_from_mbk(m: float, b: float, k: float, x0: float, v0: float, *, tfinal: float, dt: float) -> ApiResponse:
    """
    Build G_ic(s) from (m,b,k,x0,v0) using Ogata's step-equivalence and return its
    unit-step response y(t) over [0, tfinal] with step dt.
    """
    T = time_grid(tfinal, dt)
    pb = TfProblem(den=np.array([m, b, k], float), m=m, b=b, k=k, x0=x0, v0=v0)
    T_out, Y = TfSolver(pb).step_equiv_output(T)
    return ApiResponse(ok=True, data={"tf_step": {
        "T": T_out.tolist(),
        "Y": Y.tolist(),
        "labels": ["y1"],
    }})


def tf_step_api_generic(num_ic: np.ndarray, den: np.ndarray, *, tfinal: float, dt: float) -> ApiResponse:
    """
    Given G_ic(s) explicitly via (num_ic, den), return the unit-step response y(t)
    over [0, tfinal] with step dt.
    """
    T = time_grid(tfinal, dt)
    pb = TfProblem(den=np.asarray(den, float), num_ic=np.asarray(num_ic, float))
    T_out, Y = TfSolver(pb).step_equiv_output(T)
    return ApiResponse(ok=True, data={"tf_step": {
        "T": T_out.tolist(),
        "Y": Y.tolist(),
        "labels": ["y1"],
    }})


# ================================
# Optional HTTP (FastAPI) — minimal
# ================================
try:  # pragma: no cover
    from fastapi import FastAPI
    from pydantic import BaseModel

    class Compare1Req(BaseModel):
        A: list[list[float]]
        x0: list[float]
        tfinal: float
        dt: float

    class Compare2Req(BaseModel):
        A: list[list[float]]
        C: list[list[float]]
        x0: list[float]
        tfinal: float
        dt: float

    class TfOgataReq(BaseModel):
        m: float
        b: float
        k: float
        x0: float
        v0: float
        tfinal: float
        dt: float

    class TfGenericReq(BaseModel):
        num_ic: list[float]
        den: list[float]
        tfinal: float
        dt: float

    _app = FastAPI(title="icTool API", version="1.0")

    @_app.post("/compare1")
    def _compare1(req: Compare1Req):
        return compare1_api(
            np.array(req.A, float),
            np.array(req.x0, float),
            tfinal=req.tfinal,
            dt=req.dt,
        ).data

    @_app.post("/compare2")
    def _compare2(req: Compare2Req):
        return compare2_api(
            np.array(req.A, float),
            np.array(req.C, float),
            np.array(req.x0, float),
            tfinal=req.tfinal,
            dt=req.dt,
        ).data

    @_app.post("/tf-step-ogata")
    def _tf_step_ogata(req: TfOgataReq):
        return tf_step_api_from_mbk(
            req.m, req.b, req.k, req.x0, req.v0,
            tfinal=req.tfinal, dt=req.dt,
        ).data

    @_app.post("/tf-step")
    def _tf_step(req: TfGenericReq):
        return tf_step_api_generic(
            np.array(req.num_ic, float),
            np.array(req.den, float),
            tfinal=req.tfinal, dt=req.dt,
        ).data

    def get_http_app():
        return _app

except Exception:  # pragma: no cover
    def get_http_app():
        raise RuntimeError("FastAPI not installed")
