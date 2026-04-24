from __future__ import annotations
import pytest
from state_space_analysis.converterTool import cli

def test_build_parser_and_main_unit():
    p = cli.build_parser()
    ns = p.parse_args(["--num","1,0","--den","1,1,1","--no-plot"])
    req = cli.args_to_request(ns)
    assert req.num == "1,0" and req.no_plot is True

    with pytest.raises(SystemExit) as ex:
        cli.main(["--num","1,0","--den","1,1,1","--no-plot"])
    assert ex.value.code == 0
