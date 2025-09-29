"""Design presets (Ogata examples, canned models) for quick experiments."""
from __future__ import annotations
import numpy as np
from .core import SSModel, TFModel

class Presets:
    @staticmethod
    def ogata_ss_simple() -> SSModel:
        A = np.array([[0, 1], [-1, -1]], float)
        B = np.array([[0], [1]], float)
        C = np.array([[1, 0]], float)
        D = np.array([[0]], float)
        return SSModel(A, B, C, D)

    @staticmethod
    def ogata_tf_ex56() -> TFModel:
        # Example 5‑6: G(s) = (2s+1)/(s^2 + s + 1)
        return TFModel(num=np.array([2, 1], float), den=np.array([1, 1, 1], float))