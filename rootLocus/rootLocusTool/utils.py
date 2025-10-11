from __future__ import annotations
import logging, re, sys
from typing import List, Optional
import numpy as np

def make_logger(verbose: bool) -> logging.Logger:
    """
    Returns a configured logger.
    - Non-verbose: 'rootLocusTool' (INFO)
    - Verbose:     'rootLocusTool.verbose' (DEBUG)

    We use two distinct loggers to ensure a second call with verbose=True
    always returns a DEBUG-level logger, regardless of prior config, while
    also preserving the single-handler invariant on the base logger.
    """
    name = "rootLocusTool.verbose" if verbose else "rootLocusTool"
    level = logging.DEBUG if verbose else logging.INFO

    lg = logging.getLogger(name)
    lg.propagate = False  # keep logs local; avoid root handler interference

    if not lg.handlers:
        h = logging.StreamHandler(stream=sys.stderr)  # explicit stream
        h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        lg.addHandler(h)

    lg.setLevel(level)
    for h in lg.handlers:
        h.setLevel(level)

    return lg

def parse_list(s: Optional[str]) -> List[float]:
    if not s:
        return []
    return [float(x) for x in s.replace(";", ",").split(",") if x.strip() != ""]

def safe_title_to_filename(title: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", title.strip())
    return base or "case"

def parse_matrix(s: str) -> np.ndarray:
    """
    Accepts:
      "0 1 0; 0 0 1; -160 -56 -14"
      "0,1,0 | 0,0,1 | -160,-56,-14"
    """
    if s is None:
        raise ValueError("matrix string is None")
    import re as _re
    row_tokens = _re.split(r"[;|]", s.strip())
    rows = []
    for row in row_tokens:
        if not row.strip():
            continue
        items = [t for t in _re.split(r"[,\s]+", row.strip()) if t]
        rows.append([float(x) for x in items])
    if not rows:
        raise ValueError(f"could not parse matrix from '{s}'")
    ncols = {len(r) for r in rows}
    if len(ncols) != 1:
        raise ValueError(f"rows have different lengths in '{s}'")
    return np.array(rows, dtype=float)
