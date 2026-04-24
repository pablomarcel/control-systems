
from __future__ import annotations
from pathlib import Path
import json
from pid_controllers.tuningTool.design import TuningService
from pid_controllers.tuningTool.io import RulesRepository
from pid_controllers.tuningTool.core import TuningEngine
from pid_controllers.tuningTool.utils import TuningInputs

def write_rules(path: Path):
    path.write_text(json.dumps({
        "methods": {
            "ZN_step": {
                "name": "First method",
                "inputs": ["L","T"],
                "controllers": {
                    "P": { "formula": { "Kp": "T/L", "Ti": "inf", "Td": "0" } }
                }
            }
        }
    }, indent=2), encoding="utf-8")

def test_repo_and_service_lists(tmp_path: Path):
    f = tmp_path / "rules.json"
    write_rules(f)
    svc = TuningService(repo=RulesRepository(default_file=str(f)), engine=TuningEngine())
    methods = svc.list_methods()
    assert "ZN_step" in methods
    ctrls = svc.list_controllers("ZN_step")
    assert "P" in ctrls
    forms = svc.list_formulas("ZN_step")
    assert "P" in forms and "Kp" in forms["P"]

def test_service_compute(tmp_path: Path):
    f = tmp_path / "rules.json"
    write_rules(f)
    svc = TuningService(repo=RulesRepository(default_file=str(f)), engine=TuningEngine())
    res = svc.compute("ZN_step", "P", TuningInputs(L=1.0, T=2.0))
    assert res.Kp == 2.0
    assert res.Ti == float("inf")
    assert res.Kd == 0.0
