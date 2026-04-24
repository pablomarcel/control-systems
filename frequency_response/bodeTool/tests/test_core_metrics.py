from __future__ import annotations
import numpy as np
from frequency_response.bodeTool.core import Analyzer, TFBuilder

def test_margins_positive_for_typical_second_order():
    tfb = TFBuilder()
    G = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None,
                             fnum=None, fden=None, K=1.0)
    ana = Analyzer()
    w = np.logspace(-1, 2, 1000)
    m = ana.compute_margins(G, w)
    assert np.isfinite(m.pm)
    assert m.pm > 0
