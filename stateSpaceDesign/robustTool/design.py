from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np
import control as ct

from .core import Plant, Controller, Weights, LoopBuilder, FrequencyTools
from .apis import RunRequest, RunResult, SweepMetric
from .utils import log_calls

@dataclass
class RobustAnalyzer:
    req: RunRequest
    plant: Plant
    ctrl: Controller
    weights: Weights

    @log_calls()
    def build(self):
        G = self.plant.tf()
        K = self.ctrl.tf()
        L, S, T = LoopBuilder.loops(G, K)
        return G, K, L, S, T

    @log_calls()
    def run(self) -> RunResult:
        G, K, L, S, T = self.build()
        Wm, Ws, Wa = self.weights.get()

        result = RunResult(info={
            "plant": str(G),
            "controller": str(K),
            "wmin": self.req.wmin,
            "wmax": self.req.wmax,
            "npts": self.req.npts,
        })

        # Sweeps
        wmin, wmax, npts = self.req.wmin, self.req.wmax, self.req.npts
        if self.req.Wm_num and self.req.Wm_den:
            try:
                gam, wpk, *_ = FrequencyTools.hinf_sweep(ct.series(Wm, T), wmin, wmax, npts)
                result.metrics["WmT"] = SweepMetric(gamma=gam, w_peak=wpk, ok=(gam<1))
            except Exception as e:
                result.metrics["WmT"] = SweepMetric(error=str(e))

        if self.req.Ws_num and self.req.Ws_den:
            try:
                gam, wpk, *_ = FrequencyTools.hinf_sweep(ct.series(Ws, S), wmin, wmax, npts)
                result.metrics["WsS"] = SweepMetric(gamma=gam, w_peak=wpk, ok=(gam<1))
            except Exception as e:
                result.metrics["WsS"] = SweepMetric(error=str(e))

        if self.req.Wa_num and self.req.Wa_den:
            try:
                gam, wpk, *_ = FrequencyTools.hinf_sweep(ct.series(Wa, ct.series(K, S)), wmin, wmax, npts)
                result.metrics["WaKS"] = SweepMetric(gamma=gam, w_peak=wpk, ok=(gam<1))
            except Exception as e:
                result.metrics["WaKS"] = SweepMetric(error=str(e))

        # Optional step
        if self.req.step:
            try:
                t = np.arange(0, self.req.tfinal + self.req.dt, self.req.dt)
                Ty = ct.step_response(T, T=t)
                tY = np.asarray(getattr(Ty, "time", Ty[0]))
                y  = np.asarray(getattr(Ty, "outputs", Ty[1])).squeeze()

                KU = ct.series(K, S)
                Tu = ct.step_response(KU, T=t)
                tU = np.asarray(getattr(Tu, "time", Tu[0]))
                u  = np.asarray(getattr(Tu, "outputs", Tu[1])).squeeze()

                result.step_time = tY.tolist()
                result.step_y = y.tolist()
                result.step_u = u.tolist()
            except Exception as e:
                result.info["step_error"] = str(e)

        return result
