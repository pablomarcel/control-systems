"""
Simple I/O helpers for saving figures and ensuring directories.
"""
from __future__ import annotations
import os
import matplotlib.pyplot as plt
from .utils import ensure_dir, get_logger

log = get_logger(__name__)

DEFAULT_IN_DIR = "stateSpaceAnalysis/mimoTool/in"
DEFAULT_OUT_DIR = "stateSpaceAnalysis/mimoTool/out"

def out_dir(path: str | None = None) -> str:
    return ensure_dir(path or DEFAULT_OUT_DIR)

def in_dir(path: str | None = None) -> str:
    return ensure_dir(path or DEFAULT_IN_DIR)

def save_current_fig(fname: str, outpath: str | None = None) -> str:
    dirpath = out_dir(outpath)
    fpath = os.path.join(dirpath, fname)
    plt.tight_layout()
    plt.savefig(fpath, dpi=150)
    log.info(f"Saved figure: {fpath}")
    return fpath
