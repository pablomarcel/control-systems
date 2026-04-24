
import pytest
from pid_controllers.pidTool.core import Candidate, Metrics
from pid_controllers.pidTool import plotter

def test_plot_mpl_early_return(monkeypatch):
    # Force early return by toggling the flag inside plotter module
    monkeypatch.setattr(plotter, "MPL_OK", False, raising=False)
    c = Candidate(params={"K":1.0,"a":1.0},
                  metrics=Metrics(1,1,1,0,0,0,1), obj=0.0, stable=True, controller_str="Gc")
    plotter.plot_step_mpl([c], Gp=None, structure="pid_dz", top=1, save_path=None)

def test_plot_plotly_early_return(monkeypatch):
    monkeypatch.setattr(plotter, "PLOTLY_OK", False, raising=False)
    c = Candidate(params={"K":1.0,"a":1.0},
                  metrics=Metrics(1,1,1,0,0,0,1), obj=0.0, stable=True, controller_str="Gc")
    plotter.plot_step_plotly([c], Gp=None, structure="pid_dz", top=1, save_path=None)
