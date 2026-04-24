import numpy as np
from transient_analysis.responseTool.core import SecondOrderSurfaceEngine


def test_engine_overlays_shapes():
    eng = SecondOrderSurfaceEngine()
    wn = 4.0
    zetas = [0.0, 0.2, 0.5, 1.0]
    T, curves = eng.overlays(wn, zetas, tfinal=2.0, dt=0.01)
    assert T.ndim == 1 and T.size > 10
    # Curves present for each zeta; each matches |T|
    for z in zetas:
        y = curves[float(z)]
        assert isinstance(y, np.ndarray)
        assert y.shape == (T.size,)


def test_engine_mesh_shape():
    eng = SecondOrderSurfaceEngine()
    wn = 2.5
    zeta_grid = np.linspace(0.0, 1.0, 11)
    T, Z = eng.mesh(wn, zeta_grid, tfinal=1.5, dt=0.01)
    assert T.ndim == 1 and T.size > 10
    assert Z.shape == (zeta_grid.size, T.size)
