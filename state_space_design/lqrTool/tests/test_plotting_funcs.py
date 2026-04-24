import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt

from state_space_design.lqrTool.plotting import (
    plot_mpl_initial, plot_mpl_step, plot_plotly_initial, plot_plotly_step
)

def _demo_arrays():
    T = np.linspace(0, 1.0, 11)
    X = np.vstack([np.sin(T), np.cos(T)])
    Y = X[:1, :]
    U = np.zeros((1, T.size))
    return T, X, Y, U

def test_plot_mpl_creates_figs():
    T, X, Y, U = _demo_arrays()
    fig1 = plot_mpl_initial(T, X, Y, U)
    fig2 = plot_mpl_step(T, X, Y, U)
    assert hasattr(fig1, "savefig") and hasattr(fig2, "savefig")
    plt.close(fig1); plt.close(fig2)

def test_plot_plotly_creates_figs():
    T, X, Y, U = _demo_arrays()
    fig1 = plot_plotly_initial(T, X, Y, U)
    fig2 = plot_plotly_step(T, X, Y, U)
    # plotly Figure has 'to_dict'
    assert hasattr(fig1, "to_dict") and hasattr(fig2, "to_dict")
