from state_space_design.robustTool.apis import RunRequest
from state_space_design.robustTool.app import RobustApp
from state_space_design.robustTool.tools import plot as plot_mod

def test_app_run_step_and_plots_monkeypatched(monkeypatch):
    calls = {"bode_mpl":0, "bode_plotly":0, "step_mpl":0, "step_plotly":0}
    def bump(k):
        def f(*a, **kw):
            calls[k]+=1
        return f
    monkeypatch.setattr(plot_mod.Plotter, "bode_mpl", bump("bode_mpl"))
    monkeypatch.setattr(plot_mod.Plotter, "bode_plotly", bump("bode_plotly"))
    monkeypatch.setattr(plot_mod.Plotter, "step_mpl", bump("step_mpl"))
    monkeypatch.setattr(plot_mod.Plotter, "step_plotly", bump("step_plotly"))

    req = RunRequest(
        num="10 20", den="1 10 24 0",
        pid="2,5,0.1,20",
        Wm_num="0.2 1", Wm_den="0.02 1",
        Ws_num="0.5 0", Ws_den="1 0.05 0",
        Wa_num="1", Wa_den="1",
        plots="both",
        step=True, tfinal=0.5, dt=0.05,
        npts=16
    )
    res = RobustApp().run(req)
    assert res.step_time is not None and len(res.step_time) > 0
    assert calls["bode_mpl"] >= 1 and calls["bode_plotly"] >= 1
    assert calls["step_mpl"] >= 1 and calls["step_plotly"] >= 1
    assert set(["WmT","WsS","WaKS"]).issubset(res.metrics.keys())
