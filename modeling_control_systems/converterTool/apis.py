
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import control as ct
from .core import TFModel, SSModel, ConverterEngine
from .design import ConverterPretty

@dataclass(slots=True)
class ConverterConfig:
    # Mode selection: provide TF (num/den) or SS (A,B,C[,D])
    num: Optional[str] = None
    den: Optional[str] = None
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = None
    iu: int = 0
    tfinal: float = 8.0
    dt: float = 1e-3
    sympy: bool = False
    no_plot: bool = False
    # I/O
    save_json: Optional[str] = None  # path for summary JSON (optional)

@dataclass(slots=True)
class ConverterResult:
    mode: str
    tf: Optional[ct.TransferFunction] = None
    ss: Optional[ct.StateSpace] = None
    pretty_tf: Optional[str] = None
    pretty_sympy: Optional[str] = None

# -------- Programmatic helpers (pure) --------
def convert_tf_to_ss(num: np.ndarray, den: np.ndarray) -> SSModel:
    eng = ConverterEngine()
    return eng.tf_to_ss(TFModel(num, den))

def convert_ss_to_tf(A: np.ndarray, B: np.ndarray, C: np.ndarray, D: np.ndarray):
    eng = ConverterEngine()
    return eng.ss_to_tf(SSModel(A,B,C,D))
