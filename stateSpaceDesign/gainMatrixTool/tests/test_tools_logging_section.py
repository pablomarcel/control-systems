import logging
from stateSpaceDesign.gainMatrixTool.tools.logging_tools import section

def test_logging_tools_section_runs():
    logging.basicConfig(level=logging.INFO)
    with section("demo"):
        x = 1+1
        assert x == 2
