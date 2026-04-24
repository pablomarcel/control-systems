import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from state_space_analysis.mimoTool.io import out_dir, in_dir, save_current_fig
from state_space_analysis.mimoTool.utils import ensure_dir, coerce_outputs_m_by_N, get_logger

def test_dirs_and_save(tmp_path):
    # custom dirs
    o = out_dir(str(tmp_path / "outx"))
    i = in_dir(str(tmp_path / "inx"))
    assert os.path.isdir(o) and os.path.isdir(i)

    # simple fig save
    plt.figure(); plt.plot([0,1],[0,1])
    fp = save_current_fig("t.png", outpath=str(tmp_path / "outx"))
    assert os.path.exists(fp)

def test_coercions_and_logger():
    N = 5
    # 1D -> (1,N)
    arr1 = np.arange(N)
    c1 = coerce_outputs_m_by_N(arr1, N)
    assert c1.shape == (1, N)

    # (N,m) -> (m,N)
    arr2 = np.arange(6).reshape(3,2)  # treat 3 as N_time
    c2 = coerce_outputs_m_by_N(arr2, 3)
    assert c2.shape == (2,3)

    # (m,1,N) -> (m,N)
    arr3 = np.arange(8).reshape(2,1,4)
    c3 = coerce_outputs_m_by_N(arr3, 4)
    assert c3.shape == (2,4)

    # logger
    lg = get_logger("mimoTool.test", level="DEBUG")
    assert lg.level <= 10  # DEBUG or lower numeric value
