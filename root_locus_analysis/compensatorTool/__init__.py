"""
root_locus_analysis.compensatorTool

Keep this initializer lightweight so that
`python -m root_locus_analysis.compensatorTool.cli --help` is robust.
It also normalizes stdio to UTF-8 so help/log output can include
characters like the en dash used in test expectations.
"""

from __future__ import annotations

__all__ = ["__version__"]
__version__ = "0.1.0"

# --- Force UTF-8 stdio early (affects module-run entry too) ---
import sys as _sys
import io as _io

def _force_utf8_stdio() -> None:
    try:
        # Python 3.7+: reconfigure exists on TextIOWrapper
        if hasattr(_sys.stdout, "reconfigure"):
            _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            _sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            # Very old shims (unlikely on your stack, but safe)
            _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", errors="replace")
            _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        # Never block import on terminals we can't tweak
        pass

_force_utf8_stdio()
# --- end stdio normalization ---
