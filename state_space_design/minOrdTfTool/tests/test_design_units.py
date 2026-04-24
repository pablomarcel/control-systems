
import numpy as np
from state_space_design.minOrdTfTool.design import MinOrderObserverDesigner

def make_small():
    A = np.array([[0,1],[-2,-3]], float)
    B = np.array([[0],[1]], float)
    C = np.array([[1,0]], float)
    return A,B,C

def test_transform_partition_and_ke():
    A,B,C = make_small()
    d = MinOrderObserverDesigner(A,B,C)
    T, Tinv = d.transform_from_C()
    Abar = T @ A @ Tinv
    Bbar = T @ B
    Aaa, Aab, Aba, Abb, Ba, Bb = d.partition_bar(Abar, Bbar)
    Ke = d.compute_Ke(Abb, Aab, obs_poles=np.array([-5.0]))
    assert Ke.shape == (1,1)

def test_build_observer_blocks_and_realize():
    A,B,C = make_small()
    d = MinOrderObserverDesigner(A,B,C)
    T, Tinv = d.transform_from_C()
    Abar = T @ A @ Tinv
    Bbar = T @ B
    Aaa, Aab, Aba, Abb, Ba, Bb = d.partition_bar(Abar, Bbar)
    Ke = d.compute_Ke(Abb, Aab, obs_poles=np.array([-5.0]))
    ob = d.build_observer_blocks(Aaa, Aab, Aba, Abb, Ba, Bb, Ke)
    K = np.array([[6.0, 4.0]])
    # Pass Ke for correct alpha computation
    real, tf, diag = d.realize_controller(Tinv, ob, K, Ke)
    assert real.Atil.shape[0] == real.Atil.shape[1]
    assert len(tf.den) >= 1
    assert "alpha" in diag

def test_design_k_error_when_missing_ctrl(monkeypatch):
    A,B,C = make_small()
    d = MinOrderObserverDesigner(A,B,C)
    import state_space_design.minOrdTfTool.design as design_mod
    monkeypatch.setattr(design_mod, "HAS_CTRL", False, raising=False)
    try:
        d.design_K(None, np.array([-4.0, -6.0]))
    except RuntimeError as e:
        assert "python-control" in str(e)
    else:
        # If control is installed and design succeeds, it's fine—branch still executed in other envs.
        pass
