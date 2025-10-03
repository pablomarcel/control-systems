from __future__ import annotations
import subprocess, sys
from pathlib import Path

def _run(args: list[str]):
    # Execute the installed package module as CLI
    mod = 'frequencyResponse.compensatorTool.cli'
    p = subprocess.Popen([sys.executable, '-m', mod] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = p.communicate()[0]
    return p.returncode, out

def test_cli_lead_help():
    code, out = _run(['--help'])
    assert code == 0
    assert '--mode {laglead,lead}' in out

def test_cli_lead_smoke_run():
    code, out = _run(['--mode','lead','--num','4','--den','1, 2, 0','--lead_pm_target','50','--plots','bode','--backend','mpl','--no_show'])
    assert code == 0
    assert '==== DESIGN SUMMARY ====' in out
