from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from .core import StateSpaceModel, Simulator
from .design import LQRDesigner
from .io import parse_Q, parse_R, parse_vector, build_model_from_ABCD, build_model_from_tf
from .utils import controllability_rank, ensure_controllable
from .apis import LQRRunRequest, LQRRunResult

@dataclass
class LQRApp:
    req: LQRRunRequest

    def build_model(self) -> StateSpaceModel:
        if self.req.A and self.req.B:
            return build_model_from_ABCD(self.req.A, self.req.B, self.req.C, self.req.D)
        if self.req.num and self.req.den:
            return build_model_from_tf(self.req.num, self.req.den, self.req.C, self.req.D)
        raise ValueError("Provide either (A,B[,C,D]) or (num,den).")

    @ensure_controllable
    def _design(self, model: StateSpaceModel):
        Q = parse_Q(self.req.Q, model.n)
        R = parse_R(self.req.R)
        des = LQRDesigner(model)
        res = des.design(Q, R)
        return des, res

    def run(self) -> LQRRunResult:
        model = self.build_model()
        des, res = self._design(model)
        rankS = controllability_rank(model.A, model.B)
        N = None
        if self.req.step:
            N = des.prefilter(res.K, self.req.prefilter, model.C)

        # simulations (no file I/O here — just compute; plotting is delegated to CLI)
        t = np.arange(0.0, self.req.tfinal + 1e-12, self.req.dt)
        if self.req.x0:
            x0 = parse_vector(self.req.x0)
            _traj_ic = Simulator.initial(model, res.K, x0, t)  # computed to ensure path is valid

        if self.req.step:
            _traj_st = Simulator.forced_step(model, res.K, float(N), t, amp=self.req.step_amp)

        return LQRRunResult(
            K=res.K.tolist(),
            P=res.P.tolist(),
            eig_cl=np.asarray(res.eig_cl).tolist(),
            prefilter_gain=float(N) if N is not None else None,
            rank_ctrb=rankS,
            note="ok",
        )
