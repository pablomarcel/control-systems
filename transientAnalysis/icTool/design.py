# ---------------------------------
# File: transientAnalysis/icTool/design.py
# ---------------------------------
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True)
class IcDesigns:
    """Small preset library for demos and tests."""

    @staticmethod
    def second_order_example():
        A = np.array([[0, 1], [-6, -5]], float)
        x0 = np.array([2, 1], float)
        return A, x0

    @staticmethod
    def third_order_output_example():
        A = np.array([[0, 1, 0], [0, 0, 1], [-10, -17, -8]], float)
        C = np.array([[1, 0, 0]], float)
        x0 = np.array([2, 1, 0.5], float)
        return A, C, x0