import pytest, pathlib
from state_space_design.gainMatrixTool.io import BatchReader

def test_yaml_malformed_raises(tmp_path):
    yml = tmp_path / "bad.yaml"
    yml.write_text("not_a_list_or_cases_dict: 123", encoding="utf-8")
    br = BatchReader()
    with pytest.raises(SystemExit):
        br.from_yaml(str(yml))
