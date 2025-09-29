# ---------------------------------
# File: transientAnalysis/icTool/apis.py
# ---------------------------------
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Literal, Optional
import numpy as np
from .core import ICProblem, ICSolver
from .utils import time_grid

@dataclass(slots=True)
class ApiResponse:
    ok: bool
    data: Dict[str, Any]
    msg: str = ""

# Programmatic functions (dependency-free)

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

# Optional HTTP (FastAPI) — kept minimal and stateless
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

    _app = FastAPI(title="icTool API", version="1.0")

    @_app.post("/compare1")
    def _compare1(req: Compare1Req):
        return compare1_api(np.array(req.A, float), np.array(req.x0, float), tfinal=req.tfinal, dt=req.dt).data

    @_app.post("/compare2")
    def _compare2(req: Compare2Req):
        return compare2_api(np.array(req.A, float), np.array(req.C, float), np.array(req.x0, float), tfinal=req.tfinal, dt=req.dt).data

    def get_http_app():
        return _app
except Exception:  # pragma: no cover
    def get_http_app():
        raise RuntimeError("FastAPI not installed")