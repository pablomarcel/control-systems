import subprocess, sys, os, json, pathlib

def test_tool_classdiagram_writes_dot(tmp_path):
    dot_path = tmp_path / "lqrTool.dot"
    cmd = [sys.executable, "-m", "state_space_design.lqrTool.tools.tool_classdiagram", "--out", str(dot_path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert dot_path.exists()
