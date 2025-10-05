
"""
core.py — Orchestration layer gluing request/response to the designer
"""
from __future__ import annotations
from .apis import MinOrdTfRequest, MinOrdTfResponse
from .design import MinOrderObserverDesigner
from .io import export_json, pretty_dump
from .utils import parse_cplx_tokens
import numpy as np

class MinOrdTfService:
    def run(self, req: MinOrdTfRequest) -> MinOrdTfResponse:
        designer = MinOrderObserverDesigner(req.A, req.B, req.C)
        realization, tf, payload = designer.full_design(
            obs_poles=req.obs_poles,
            K_row=req.K,
            K_poles_tokens=req.K_poles_tokens,
            allow_pinv=req.allow_pinv,
        )

        json_path = None
        if req.export_json:
            json_path = export_json(payload, req.export_json)

        if req.pretty:
            print("\n== minOrdTfTool results ==")
            print(pretty_dump(payload, precision=req.precision))

        return MinOrdTfResponse(tf_num=tf.num, tf_den=tf.den, json_path=json_path)
