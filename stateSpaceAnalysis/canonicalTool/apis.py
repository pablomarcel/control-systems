
from __future__ import annotations
from typing import Any, Dict
from .app import CanonicalToolApp
from .design import CompareOptions

class CanonicalAPI:
    def __init__(self):
        self._app = CanonicalToolApp()

    def compare(self, num, den, tfinal=8.0, dt=1e-3, symbolic=False, backend="mpl", show=True, save=None) -> Dict[str, Any]:
        opts = CompareOptions(tfinal=tfinal, dt=dt, symbolic=symbolic, backend=backend, show=show, save=save)
        res = self._app.compare(num=num, den=den, opts=opts)
        return {
            "tf_equal": res.tf_equal,
            "symbolic": res.symbolic,
        }
