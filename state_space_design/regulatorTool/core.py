#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core.py — core dataclasses for plant representation and regulator parameters/results.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple
import numpy as np
import control as ct

@dataclass
class Plant:
    num: np.ndarray
    den: np.ndarray
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: float

@dataclass
class RegulatorParams:
    K_poles: Optional[np.ndarray] = None
    obs_poles: Optional[np.ndarray] = None
    ts: Optional[float] = None
    undershoot: Optional[Tuple[float, float]] = None
    obs_speed_factor: float = 5.0

@dataclass
class SimulationSpec:
    x0: Optional[np.ndarray] = None
    e0: Optional[np.ndarray] = None
    t_final: float = 8.0
    dt: float = 0.01

@dataclass
class RegulatorDesignResult:
    K: np.ndarray
    Ke: np.ndarray
    Ahat: np.ndarray
    Bhat: np.ndarray
    Fhat: np.ndarray
    Atil: np.ndarray
    Btil: np.ndarray
    Ctil: np.ndarray
    Dtil: np.ndarray
    Gc: ct.TransferFunction
    G: ct.TransferFunction
    L: ct.TransferFunction
    T: ct.TransferFunction

@dataclass
class Signals:
    t: np.ndarray
    X: np.ndarray   # states (n, N)
    E: np.ndarray   # observer error states (r, N)
    U: np.ndarray   # control input (N,)
    Y: np.ndarray   # output (N,)
