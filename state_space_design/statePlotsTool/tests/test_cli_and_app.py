
import json
from state_space_design.statePlotsTool.cli import main as cli_main
from state_space_design.statePlotsTool.app import StatePlotsApp
from state_space_design.statePlotsTool.apis import StatePlotsAPI

def test_cli_main_ic(capsys, tmp_path):
    ctrl = {"mode":"K","A":[[0,1],[-2,-3]],"B":[[0],[1]],"K":[[0,0]]}
    ctrl_path = tmp_path / "c.json"
    ctrl_path.write_text(json.dumps(ctrl))
    cli_main(["--data", str(ctrl_path), "--scenario", "ic", "--x0", "1 0", "--t", "0:0.1:0.2",
              "--backend", "none", "--save_csv", "ic.csv", "--no_show"])
    out = capsys.readouterr().out
    assert "Scenario: ic" in out

def test_app_wrapper(tmp_path):
    api = StatePlotsAPI()
    app = StatePlotsApp(api=api)
    io = {"Acl":[[0,1],[-2,-3]],"Bcl":[[0],[1]],"C":[[1,0]],"D":[[0]]}
    io_path = tmp_path / "io.json"
    io_path.write_text(json.dumps(io))
    res = app.run(data=io_path, scenario="step", what="y", t="0:0.1:0.2",
                  backend="none", save_csv="s.csv", no_show=True)
    assert res["scenario"] == "step" and "csv" in res["paths"]
