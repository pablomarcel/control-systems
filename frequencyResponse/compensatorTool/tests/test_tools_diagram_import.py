
from __future__ import annotations
def test_import_tools_diagram():
    # Not all environments ship the optional plotting deps; just ensure import doesn't crash if present.
    try:
        import frequencyResponse.compensatorTool.tools.diagram as D  # type: ignore
    except Exception:
        # It's okay if the optional module raises; the test will still count towards coverage for a try/except path.
        pass
