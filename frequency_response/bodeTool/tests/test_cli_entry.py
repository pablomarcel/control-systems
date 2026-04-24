
from __future__ import annotations
import sys
from frequency_response.bodeTool import cli as cli_mod

def test_cli_main_smoke(capsys, monkeypatch, tmp_path):
    # Avoid opening GUI windows by not plotting; just do JSON
    argv = ["--num","1","--den","1, 0.8, 1","--save-json", str(tmp_path/"out.json")]
    cli_mod.main(argv)
    out = capsys.readouterr().out
    assert "Frequency-Response Summary" in out
    assert (tmp_path/"out.json").exists()
