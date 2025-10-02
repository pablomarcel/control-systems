from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
import numpy as np

# Verbose toggle used across modules (simple, testable)
VERBOSE: bool = False

def set_verbose(flag: bool) -> None:
    global VERBOSE
    VERBOSE = bool(flag)

def info(msg: str) -> None:
    if VERBOSE:
        print(f"INFO: {msg}", flush=True)

def ensure_dir(p: str | Path) -> str:
    Path(p).mkdir(parents=True, exist_ok=True)
    return str(p)

def ensure_in_dir(pkg_root: str | Path) -> str:
    return ensure_dir(Path(pkg_root) / "in")

def ensure_out_dir(pkg_root: str | Path) -> str:
    return ensure_dir(Path(pkg_root) / "out")

def np2list(x):
    arr = np.array(x)
    if np.iscomplexobj(arr):
        return [[float(np.real(v)), float(np.imag(v))] for v in arr.ravel().tolist()]
    return [float(v) for v in arr.ravel().tolist()]
