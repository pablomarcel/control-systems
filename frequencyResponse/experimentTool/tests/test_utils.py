from __future__ import annotations
import numpy as np
from pathlib import Path

from frequencyResponse.experimentTool.utils import ensure_dir, np2list, set_verbose, info

def test_np2list_scalars_vectors_and_complex():
    assert np2list([1,2,3]) == [1.0,2.0,3.0]
    z = np.array([1+2j, 3-4j])
    out = np2list(z)
    assert out == [[1.0,2.0],[3.0,-4.0]]

def test_ensure_dir(tmp_path: Path, capsys):
    p = tmp_path / "a" / "b"
    s = ensure_dir(p)
    assert Path(s).exists()

def test_info_verbose(capsys):
    set_verbose(True)
    info("hello")
    set_verbose(False)
