
"""
app.py — Application facade for minOrdTfTool
"""
from __future__ import annotations
from .apis import MinOrdTfRequest, MinOrdTfResponse
from .core import MinOrdTfService
import numpy as np

class MinOrdTfApp:
    def __init__(self):
        self.service = MinOrdTfService()

    def run(self, **kwargs) -> MinOrdTfResponse:
        req = MinOrdTfRequest(**kwargs)
        return self.service.run(req)
