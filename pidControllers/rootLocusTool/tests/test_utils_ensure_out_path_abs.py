from __future__ import annotations
from pidControllers.rootLocusTool.utils import ensure_out_path
from pathlib import Path

def test_ensure_out_path_absolute(tmp_path):
    p = tmp_path / "abs.txt"
    out = ensure_out_path(str(p))
    assert out == str(p)
    assert (tmp_path).exists()
