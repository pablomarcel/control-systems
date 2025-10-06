
import numpy as np
from stateSpaceDesign.observerStatePlotTool.core import ObserverStateProcessor

def test_reconstruct_and_choose():
    proc = ObserverStateProcessor()
    t = np.array([0.0, 0.5, 1.0])
    X = np.array([[1.0, 0.5, 0.2],
                  [0.0,-0.2,-0.1]])
    E = np.array([[0.8, 0.4, 0.2],
                  [0.1,-0.1,-0.05]])
    payload = {
        "K": [1.0, 2.0],
        "C": [[1.0, 0.0]],
        "simulation": {}  # so reconstruct reads from payload.simulation for u,y (None)
    }
    u, y = proc.reconstruct_u_y_if_missing(payload, t, X, E)
    assert u is not None and y is not None
    labels, series = proc.choose_series(["x","e","err","y","u"], X, E, y, u)
    assert "x1" in labels and "e2" in labels and "x-e1" in labels and "y" in labels and "u" in labels
    assert len(series) == len(labels)
