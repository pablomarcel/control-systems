from __future__ import annotations
import numpy as np
import control as ct
from frequencyResponse.bodeTool.core import Analyzer
from frequencyResponse.bodeTool.core import TFBuilder
from frequencyResponse.bodeTool.apis import Margins

def test_margins_positive_for_typical_second_order():
    tfb = TFBuilder()
    G = tfb.build_from_modes(num="1", den="1, 0.8, 1", gain=None, zeros=None, poles=None,
                             fnum=None, fden=None, K=1.0)
    ana = Analyzer()
    # frequency grid around 0.1..100
    w = np.logspace(-1, 2, 1000)
    m = ana.compute_margins(G, w)
    assert np.isfinite(m.pm)
    # classic 2nd-order with zeta=0.4 has PM > 0 (unity feedback assumption)
    assert m.pm > 0
