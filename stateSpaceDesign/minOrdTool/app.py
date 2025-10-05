# -*- coding: utf-8 -*-
"""
app.py — Orchestration layer for stateSpaceDesign.minOrdTool

- Parses request, invokes service, writes JSON output
- Ensures JSON is safe for NumPy/complex types
"""

from __future__ import annotations

import os
import json
import logging
import datetime

from .apis import MinOrdRunRequest, MinOrdRunResult
from .io import parse_mat, parse_poles_tokens, _split_list_any
from .design import MinOrdAppService
from .utils import to_jsonable  # ensure JSON-safe serialization

DEFAULT_OUT_DIR = os.path.join("stateSpaceDesign", "minOrdTool", "out")


def run_app(req: MinOrdRunRequest) -> MinOrdRunResult:
    """
    Execute a run given a MinOrdRunRequest and return MinOrdRunResult.
    """
    logging.basicConfig(
        level=(logging.DEBUG if req.verbose else logging.INFO),
        format="%(levelname)s: %(message)s",
    )

    # --- Parse inputs ---
    A = parse_mat(req.A)
    C = parse_mat(req.C)
    B = parse_mat(req.B) if req.B is not None else None

    obs_poles = parse_poles_tokens(req.poles)
    K = parse_mat(req.K) if req.K is not None else None
    kp = None
    if req.K_poles:
        # Accept either list of tokens or a single string with CSV/space
        kp = parse_poles_tokens(req.K_poles if isinstance(req.K_poles, list) else _split_list_any(req.K_poles))

    # --- Invoke service ---
    service = MinOrdAppService(precision=req.precision, verbose=req.verbose)
    payload = service.design_observer(
        A=A,
        C=C,
        poles=obs_poles,
        B=B,
        allow_pinv=req.allow_pinv,
        pretty=req.pretty,
        K=K,
        K_poles=kp,
    )

    # --- Output path ---
    if req.export_json:
        json_path = req.export_json
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(DEFAULT_OUT_DIR, f"minOrd_{ts}.json")

    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # --- Write JSON (JSON-safe conversion for robustness) ---
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(to_jsonable(payload), f, indent=2)

    return MinOrdRunResult(json_path=json_path, payload=payload)
