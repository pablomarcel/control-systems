
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import pytest

@pytest.fixture(autouse=True)
def _no_show(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda *a, **k: None)
    yield
