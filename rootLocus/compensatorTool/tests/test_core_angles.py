# modernControl/rootLocus/compensatorTool/tests/test_core_angles.py
from __future__ import annotations
import numpy as np
import control as ct

from rootLocus.compensatorTool.core import (
    angle_deficiency,
    lead_from_bisector_validated,
    lag_angle_mag,
)


def test_angle_deficiency_positive():
    G = ct.tf([4.0], [0.5, 1.0, 0.0])  # 4 / (s(s+0.5))
    sstar = complex(-2.5, 4.330127)    # ζ=0.5, ωn=5 → σ=-2.5, ωd≈4.33
    phi = angle_deficiency(G, sstar)
    assert 0 < phi < np.pi


def test_bisector_auto_repair_feasible():
    sstar = complex(-2.5, 4.330127)
    phi = np.deg2rad(40.0)
    z, p = lead_from_bisector_validated(sstar, phi)
    assert p > z > 0


def test_lag_angle_near_zero_when_T2_large():
    sstar = complex(-2.5, 4.330127)
    ang, mag = lag_angle_mag(sstar, beta=10.0, T2=100.0)
    # Large T2 yields a small negative lag angle at s*; keep a practical bound.
    # Empirically ≈ -0.089° for these values, so allow a small margin.
    assert -0.2 <= ang <= 0.0
    # Magnitude should remain essentially unity.
    assert 0.95 <= mag <= 1.05
