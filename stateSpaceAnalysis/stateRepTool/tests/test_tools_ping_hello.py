from stateSpaceAnalysis.stateRepTool.tools.tool_1 import hello
from stateSpaceAnalysis.stateRepTool.tools.tool_2 import ping

def test_tools_smoke():
    assert hello() == "tool_1 ready"
    assert ping() == "tool_2 pong"
