
import os
from state_space_design.minOrdTool.tools import class_diagram as cd

def test_class_diagram_fallback_dot(tmp_path, monkeypatch):
    # Force 'dot' to be unavailable so we exercise DOT fallback
    monkeypatch.setattr(cd.shutil, "which", lambda _: None)
    out_png = tmp_path/"minOrdTool_classes.png"
    # Change CWD so the default relative output lands under tmp_path
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        cd.main()
    finally:
        os.chdir(cwd)
    # Expect a .dot since dot not available
    dot_path = (tmp_path/"state_space_design/minOrdTool/out/minOrdTool_classes.dot")
    assert dot_path.exists()
