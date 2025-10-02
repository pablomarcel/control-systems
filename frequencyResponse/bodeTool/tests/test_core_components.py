
from __future__ import annotations
import numpy as np
import math
import control as ct
from frequencyResponse.bodeTool.core import TFBuilder, FrequencyGrid, Analyzer

def test_tf_builder_three_modes():
    tfb = TFBuilder()
    # Coeff mode
    Gc = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None, fnum=None, fden=None, K=1.0)
    assert isinstance(Gc, ct.TransferFunction)

    # Zeros/poles mode
    Gzp = tfb.build_from_modes(num=None, den=None, gain=2.0, zeros="-1", poles="-2, -3", fnum=None, fden=None, K=1.0)
    assert isinstance(Gzp, ct.TransferFunction)

    # Factorized mode with K
    Gf = tfb.build_from_modes(num=None, den=None, gain=None, zeros=None, poles=None,
                              fnum="K (s+1)", fden="s (s+5)", K=3.0)
    assert isinstance(Gf, ct.TransferFunction)

def test_frequency_grid_breaks_and_make():
    tfb = TFBuilder()
    G = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None, fnum=None, fden=None, K=1.0)
    fg = FrequencyGrid()
    br = fg.break_freqs(G)
    # second-order poles magnitude around 1 -> expect at least one break near 1
    assert br.size >= 1
    grid = fg.make(G, None, None, 200)
    assert len(grid) == 200
    assert grid[0] > 0 and grid[-1] > grid[0]

def test_analyzer_margins_closedloop_nyquist():
    tfb = TFBuilder()
    G = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None, fnum=None, fden=None, K=1.0)
    fg = FrequencyGrid()
    w = fg.make(G, None, None, 1000)
    az = Analyzer()
    m = az.compute_margins(G, w)
    assert math.isfinite(m.pm)
    cl = az.closedloop_metrics(G, w)
    assert math.isfinite(cl.Mr_db) or cl.Mr_db == float("-inf")
    N = az.nyq_encirclements(G, w)
    assert isinstance(N, int)
