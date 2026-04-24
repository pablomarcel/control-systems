
"""
apis.py — Request/Response dataclasses for minOrdTfTool
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import numpy as np

@dataclass
class MinOrdTfRequest:
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    obs_poles: np.ndarray
    K: Optional[np.ndarray] = None
    K_poles_tokens: Optional[List[str]] = None
    allow_pinv: bool = False
    pretty: bool = False
    precision: int = 6
    export_json: Optional[str] = None

@dataclass
class MinOrdTfResponse:
    tf_num: np.ndarray
    tf_den: np.ndarray
    json_path: Optional[str] = None
