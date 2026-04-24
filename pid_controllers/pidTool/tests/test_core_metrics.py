from __future__ import annotations
import numpy as np
import pytest
try:
    import control as ct
except Exception:
    ct = None

from pid_controllers.pidTool.core import compute_metrics, controller_tf

@pytest.mark.skipif(ct is None, reason="python-control not installed")
def test_compute_metrics_basics():
    Gp = ct.tf([1],[1,1])  # 1/(s+1)
    Gc = controller_tf("pd", {"Kp":1.0, "Kd":0.0})
    T = ct.feedback(Gc*Gp, 1)
    m = compute_metrics(T, tfinal=5.0, dt=0.005)
    assert m.itae >= 0
    assert m.ise >= 0
    assert m.tfinal_used > 0
