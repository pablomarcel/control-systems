# pidControllers/rootLocusTool/utils.py
from __future__ import annotations
import os
import math
from typing import Optional, Iterable, List


def ensure_out_path(path: Optional[str]) -> Optional[str]:
    """
    Return an absolute path suitable for writing files.

    Behavior:
      - None                     -> None
      - Absolute path            -> ensure parent dirs, return as-is
      - Relative path            -> anchor under *current working directory* ./out/
                                    (prefix 'out/' if not provided), ensure parent
                                    dirs, and return an absolute path

    This mirrors the behavior expected by the tests and by the original
    standalone tool (i.e., relative outputs are created under ./out of CWD).
    """
    if path is None:
        return None

    # Absolute path: ensure parent dirs and return unchanged
    if os.path.isabs(path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        return path

    # Normalize leading './'
    rel = path[2:] if path.startswith("./") else path

    # If caller didn't explicitly put the file under 'out/', do it for them.
    # Handle both POSIX and Windows separators.
    if not (rel.startswith("out/") or rel.startswith("out" + os.sep)):
        rel = os.path.join("out", rel)

    # Build absolute path from current working directory and ensure parents
    abs_path = os.path.abspath(rel)
    os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
    return abs_path


def parse_poly(arg: Optional[str | Iterable[float]]) -> List[float] | None:
    """
    Parse a polynomial coefficient specification, accepting:
      - None -> None
      - Iterable of numbers -> list[float]
      - String with CSV or space-separated numbers -> list[float]
    """
    if arg is None:
        return None
    if isinstance(arg, (list, tuple)):
        return [float(x) for x in arg]
    parts = [p for p in str(arg).replace(",", " ").split() if p.strip()]
    return [float(p) for p in parts]


def complex_arg(z: complex) -> float:
    """Return the complex argument (phase) of z in radians."""
    return math.atan2(z.imag, z.real)
