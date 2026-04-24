
from pid_controllers.pidTool.tools.diagram_tool import emit_mermaid

def test_emit_mermaid_basic():
    mmd = emit_mermaid([("core","PIDDesignerApp"),("design","SearchEngine")])
    assert "classDiagram" in mmd
    assert "class PIDDesignerApp" in mmd
