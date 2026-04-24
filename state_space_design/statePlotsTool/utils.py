# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import functools
import os

PKG_ROOT = Path(__file__).resolve().parent
DEFAULT_IN_DIR  = PKG_ROOT / "in"
DEFAULT_OUT_DIR = PKG_ROOT / "out"

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def resolve_out_path(filename: str | None, default_name: str, out_dir: Path | None = None) -> Path:
    out_dir = Path(out_dir) if out_dir else DEFAULT_OUT_DIR
    ensure_dir(out_dir)
    base = Path(filename) if filename else Path(default_name)
    return out_dir / base.name

def package_rel(pathlike: str | os.PathLike) -> Path:
    """Resolve a path relative to the package root."""
    p = Path(pathlike)
    return p if p.is_absolute() else (PKG_ROOT / p)

def with_outdir(func):
    """Decorator that injects a default out_dir kwarg when not provided."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'out_dir' not in kwargs or kwargs['out_dir'] is None:
            kwargs['out_dir'] = DEFAULT_OUT_DIR
        return func(*args, **kwargs)
    return wrapper
