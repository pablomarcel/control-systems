from pathlib import Path
import json, os
from pidControllers.tuningTool.io import RulesRepository, RulesLoadError
from pidControllers.tuningTool.tools.tool_paths import IN_DIR, PKG_ROOT

def test_repo_resolve_filename_and_in_prefix(tmp_path):
    repo = RulesRepository()
    # filename under in/
    p1 = (IN_DIR / "x1.json"); p1.write_text('{"ok":1}', encoding="utf-8")
    d1 = repo.read_json("x1.json"); assert d1["ok"] == 1
    # explicit in/ prefix from package root
    p2 = (IN_DIR / "x2.json"); p2.write_text('{"ok":2}', encoding="utf-8")
    d2 = repo.read_json("in/x2.json"); assert d2["ok"] == 2

def test_repo_resolve_abs_and_errors(tmp_path):
    repo = RulesRepository()
    bad = tmp_path / "nope.json"
    try:
        repo.read_json(str(bad))
    except RulesLoadError as e:
        assert "not found" in str(e)

    # malformed
    m = tmp_path / "bad.json"; m.write_text("{ not_json: true,", encoding="utf-8")
    try:
        repo.read_json(str(m))
    except RulesLoadError as e:
        assert "Failed to parse" in str(e)
