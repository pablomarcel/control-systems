from stateSpaceAnalysis.mimoTool.app import MIMOToolApp

def test_app_wrappers():
    app = MIMOToolApp()
    desc = app.run_describe("two_tank")
    assert "A" in desc and "poles" in desc

    # run sigma save
    p = app.run_sigma("two_tank", save=True, out_name="app_sigma.png")
    assert isinstance(p, str) and p.endswith("app_sigma.png")

    # run steps (no save to keep fast)
    paths = app.run_steps("two_tank", tfinal=1.0, dt=0.5, save=False)
    assert paths == []  # when not saving, we return empty list
