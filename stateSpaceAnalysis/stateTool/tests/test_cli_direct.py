
from __future__ import annotations
import json
from stateSpaceAnalysis.stateTool import cli as cli_mod

def test_cli_main_direct_state(capsys):
    argv = ["--A","0 1; -2 -3","--B","0;1","--C","3 1","--D","0","--mode","all","--log","WARNING"]
    rc = cli_mod.main(argv)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "obs" in data["results"] and "state" in data["results"]

def test_cli_main_direct_tf(capsys):
    argv = ["--tf","(s+3)/(s^2+3*s+2)","--mode","obssplane","--log","WARNING"]
    rc = cli_mod.main(argv)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "obssplane" in data["results"]
