
import pytest
from pidControllers.pidTool import utils

def test_ensure_out_dir_tmp(tmp_path, monkeypatch):
    # force a temp dir
    d = utils.ensure_out_dir(str(tmp_path / "out_here"))
    assert d == str(tmp_path / "out_here")
    assert (tmp_path / "out_here").exists()

def test_parse_list_helpers():
    assert utils.parse_list_of_floats("1, 2  3") == [1.0, 2.0, 3.0]
    assert utils.parse_list_of_floats(None) == []
    assert utils.parse_list_of_complex("1+2j, 3-4i  5") == [complex(1,2), complex(3,-4), 5+0j]
    assert utils.parse_list_of_complex(None) == []
