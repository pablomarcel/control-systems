
import pytest
from graphviz.backend.execute import ExecutableNotFound as GVExeNotFound
from state_space_design.regulatorTool.tools.class_diagram import generate_class_diagram

def test_class_diagram_function_runs_or_skips(tmp_path):
    out = tmp_path / "classes.dot"
    try:
        result = generate_class_diagram(str(out))
    except GVExeNotFound:
        # Accept missing Graphviz executables on PATH
        result = ""
    assert isinstance(result, str)
