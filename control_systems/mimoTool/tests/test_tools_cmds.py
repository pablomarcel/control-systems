
from __future__ import annotations
import subprocess, sys

def test_tool_sanity_exec():
    """Graphviz is unavailable on this machine; only run the sanity tool."""
    res = subprocess.run([sys.executable, "-c", "from control_systems.mimoTool.tools.tool_sanity import main; main()"],
                         capture_output=True, text=True)
    assert res.returncode == 0
    assert "poles" in res.stdout
