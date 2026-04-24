
from __future__ import annotations
import numpy as np, pathlib, json
from transient_analysis.responseTool.utils import parse_vector, parse_matrix, parse_zetas_list, time_grid
from transient_analysis.responseTool.io import save_json, save_plot, dump_ndarray
import matplotlib.pyplot as plt

import pytest

def test_parsers_and_timegrid():
    assert (parse_vector("1, 2,3").tolist() == [1.0,2.0,3.0])
    m = parse_matrix("1 2; 3 4")
    assert m.shape == (2,2) and float(m[1,1]) == 4.0
    zlist = parse_zetas_list(None)
    assert zlist and isinstance(zlist, list)
    T = time_grid(0.3, 0.1)
    assert float(T[0]) == 0.0 and T[-1] == pytest.approx(0.3, abs=1e-12)

def test_io_helpers(tmp_path):
    p = tmp_path / "a.json"
    save_json(p, {"x": 1})
    assert json.loads(p.read_text())["x"] == 1
    plt.figure(); plt.plot([0,1],[0,1])
    png = tmp_path / "p.png"
    save_plot(png); assert png.exists()
    arrp = tmp_path / "a.npy"
    dump_ndarray(arrp, np.array([1,2,3.0]))
    assert arrp.exists()
