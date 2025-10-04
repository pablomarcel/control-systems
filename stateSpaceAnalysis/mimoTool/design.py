"""
Plant builders and pre-configured examples.
"""
from __future__ import annotations
import numpy as np
import control as ct
from .core import MIMOSystem

class PlantFactory:
    @staticmethod
    def two_tank() -> MIMOSystem:
        A1, A2 = 0.05, 0.04
        k1, k2 = 0.0015, 0.0012
        kc = 0.0008
        A = np.array([
            [-(k1 + kc)/A1,  kc/A1],
            [ kc/A2,        -(k2 + kc)/A2]
        ])
        B = np.array([[1.0/A1, 0.0],
                      [0.0,    1.0/A2]])
        C = np.eye(2)
        D = np.zeros((2,2))
        return MIMOSystem(ct.ss(A,B,C,D))

    @staticmethod
    def two_zone_thermal() -> MIMOSystem:
        C1, C2 = 800.0, 600.0
        ka1, ka2 = 10.0, 8.0
        kc = 6.0
        A = np.array([
            [-(ka1 + kc)/C1,  kc/C1],
            [ kc/C2,         -(ka2 + kc)/C2]
        ])
        B = np.array([[1.0/C1, 0.0],
                      [0.0,    1.0/C2]])
        C = np.eye(2)
        D = np.zeros((2,2))
        return MIMOSystem(ct.ss(A,B,C,D))
