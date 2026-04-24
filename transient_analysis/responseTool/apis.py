from __future__ import annotations
from pathlib import Path
import numpy as np
from .app import ResponseToolApp, ResponseResult

# Simple, dependency‑free programmatic façades (nice for tests and notebooks)

def ramp_ss_api(A, B, C, D, *, tfinal: float = 10.0, dt: float = 0.01, root: str | Path = ".") -> ResponseResult:
    app = ResponseToolApp(root=Path(root), show_plots=False)
    return app.compute_unit_ramp_ss(A, B, C, D, tfinal=tfinal, dt=dt)


def lsim_tf_api(num, den, *, u: str = "ramp", tfinal: float = 10.0, dt: float = 0.01, root: str | Path = ".") -> ResponseResult:
    app = ResponseToolApp(root=Path(root), show_plots=False)
    return app.simulate_tf_input(num, den, u=u, tfinal=tfinal, dt=dt)