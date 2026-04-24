from __future__ import annotations
import json
from typing import Optional, Dict, List
import sympy as sp
from .apis import StateTransRequest, StateTransResult
from .core import StateTransitionEngine
from .utils import sym_t

class StateTransApp:
    """High-level orchestrator: parse → build A → compute Φ(t) → format/export."""
    def __init__(self, req: StateTransRequest):
        self.req = req
        self.engine = StateTransitionEngine(canonical=req.canonical)

    def run(self) -> StateTransResult:
        msgs: List[str] = []
        # Parse
        num_desc, den_desc = self.engine.parse_inputs(self.req.tf, self.req.num, self.req.den, self.req.example)
        # Build A
        A = self.engine.build_A(num_desc, den_desc)
        # Compute Φ(t)
        Phi = self.engine.phi_symbolic(A)
        Phi_inv = self.engine.phi_inverse_symbolic(A) if self.req.inverse else None

        t = sym_t()
        Phi_eval = Phi_inv_eval = None
        if self.req.eval_time is not None:
            Phi_eval = sp.Matrix(Phi.subs(t, float(self.req.eval_time)))
            if Phi_inv is not None:
                Phi_inv_eval = sp.Matrix(Phi_inv.subs(t, float(self.req.eval_time)))

        res = StateTransResult(
            A=A, canonical=self.req.canonical, Phi=Phi, Phi_inv=Phi_inv,
            Phi_eval=Phi_eval, Phi_inv_eval=Phi_inv_eval, messages=msgs
        )
        return res
