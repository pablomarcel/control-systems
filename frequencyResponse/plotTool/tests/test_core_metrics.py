from __future__ import annotations
import numpy as np
import control as ct
from frequencyResponse.plotTool.core import make_grid, compute_margins, closedloop_metrics

def test_metrics_simple():
    # Simple TF: K/(s(s+1)(0.5s+1)) with K=1
    num = [1.0]; den = np.polymul([1,0], np.polymul([1,1],[0.5,1]))
    G = ct.tf(num, den)
    w = make_grid(G, 0.05, 10.0, 400)
    m = compute_margins(G, w)
    cl = closedloop_metrics(G, w)
    assert np.isfinite(m.pm) and m.pm > 0 or np.isnan(m.pm)
    assert np.isfinite(cl.Mr_db)
