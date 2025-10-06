
import importlib
from stateSpaceDesign.regulatorTool.app import _maybe_plot
from stateSpaceDesign.regulatorTool.apis import RegulatorRunRequest, RegulatorService

def test_app_maybe_plot_doesnt_plot_when_backends_false(monkeypatch):
    # Build a service
    req = RegulatorRunRequest(
        num=[10,20], den=[1,10,24,0], plots="none"
    )
    svc = RegulatorService(req)
    # Disable backends via monkeypatch at module-level flags
    import stateSpaceDesign.regulatorTool.app as appmod
    monkeypatch.setattr(appmod, "HAS_MPL", False, raising=False)
    monkeypatch.setattr(appmod, "HAS_PLOTLY", False, raising=False)
    # Call with show=False and no saving
    _maybe_plot(svc, show=False, save_prefix=None, rl_axes=(-10,2,-5,5), rl_k="auto", backend="both", ply_width=0)
