from __future__ import annotations
from pidControllers.rootLocusTool.utils import ensure_out_path

def test_ensure_out_path_none():
    assert ensure_out_path(None) is None
