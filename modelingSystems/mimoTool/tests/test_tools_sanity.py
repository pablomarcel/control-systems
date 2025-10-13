
from __future__ import annotations
import subprocess, sys

def test_tool_sanity_exec():
    res = subprocess.run([sys.executable, "-c", "from modelingSystems.mimoTool.tools.tool_sanity import main; main()"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "poles" in res.stdout
