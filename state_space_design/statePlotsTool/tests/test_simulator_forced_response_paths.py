
import numpy as np
from state_space_design.statePlotsTool.core import Simulator
from state_space_design.statePlotsTool.io import IOJSON

def test_fr_object_path(monkeypatch):
    class Resp:
        def __init__(self, t, y, x):
            self.time=t; self.outputs=y; self.states=x
    def fake_forced_response(sys, T, U):
        y = np.vstack([np.sin(T)])
        x = np.vstack([np.cos(T), np.sin(T)])
        return Resp(T, y, x)
    monkeypatch.setattr("control.forced_response", fake_forced_response)
    io = IOJSON(
        Acl=np.array([[0,1],[-2,-3]]),
        Bcl=np.array([[0],[1]]),
        C=np.array([[1,0]]),
        D=np.array([[0]]),
        r=1.0,
        state_names=["x1","x2"],
        output_names=["y1"]
    )
    T = np.linspace(0,1,6)
    res = Simulator.step(io, T, what='both')
    assert len(res.series) == 3 and res.kind == 'both'

def test_states_via_outputs_path(monkeypatch):
    def fr_io(sys, T, U):
        return (T, np.vstack([T]),)
    monkeypatch.setattr("control.forced_response", fr_io)
    monkeypatch.setattr("state_space_design.statePlotsTool.core.Simulator._simulate_states_via_output",
                        lambda Acl,Bcl,T,U: (T, np.vstack([T, T**2])))
    io = IOJSON(
        Acl=np.array([[0,1],[-2,-3]]),
        Bcl=np.array([[0],[1]]),
        C=np.array([[1,0]]),
        D=np.array([[0]]),
        r=1.0,
        state_names=["x1","x2"],
        output_names=["y1"]
    )
    T = np.linspace(0,1,6)
    res = Simulator.step(io, T, what='both')
    assert len(res.series) == 3
