from stateSpaceAnalysis.mimoTool.tools.tool_plotting import figure
from stateSpaceAnalysis.mimoTool.tools.tool_classdiagram import emit_basic_diagram

def test_plotting_helper():
    fig = figure("Hello")
    assert fig is not None

def test_classdiagram_handles_no_graphviz():
    # Should not raise even if `dot` is missing; returns None in that case.
    out = emit_basic_diagram()
    assert (out is None) or (isinstance(out, str) and out.endswith(".png"))
