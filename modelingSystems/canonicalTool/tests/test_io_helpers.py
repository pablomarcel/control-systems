
from pathlib import Path
import json
from modelingSystems.canonicalTool.io import parse_coeffs, ensure_out_dir, write_json

def test_parse_and_write(tmp_path):
    assert parse_coeffs("1, 2,  3") == [1.0, 2.0, 3.0]
    outd = ensure_out_dir(tmp_path / "sub")
    assert outd.exists()
    p = tmp_path / "sub" / "obj.json"
    write_json({"a":1}, p)
    data = json.loads(p.read_text())
    assert data["a"] == 1
