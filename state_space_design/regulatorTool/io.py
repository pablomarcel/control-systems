#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
io.py — filesystem helpers for regulatorTool.
"""

from __future__ import annotations
import os, json
from dataclasses import asdict, is_dataclass
from typing import Any

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_IN_DIR  = os.path.join(PKG_DIR, "in")
DEFAULT_OUT_DIR = os.path.join(PKG_DIR, "out")

def ensure_dir(d: str) -> None:
    os.makedirs(d, exist_ok=True)

def out_path(*parts: str, out_dir: str | None = None) -> str:
    """
    Build a path under the tool's OUT directory (package-relative) unless a custom out_dir is specified.
    Always ensures the directory exists.
    """
    d = DEFAULT_OUT_DIR if out_dir is None else out_dir
    ensure_dir(d)
    return os.path.join(d, *parts)

def resolve_save_prefix(prefix: str | None) -> str | None:
    """
    Convert a user-supplied save prefix to an absolute path we can safely append suffixes to.
    Rules:
      - None          -> None
      - Absolute path -> return as-is (ensure parent exists)
      - Starts with 'out' or './out' -> resolve under package OUT dir
      - Bare basename -> place under package OUT dir
      - Relative path with subdirs (e.g., 'figs/run1') -> resolve relative to CWD (ensure parent)
    """
    if not prefix:
        return None
    if os.path.isabs(prefix):
        ensure_dir(os.path.dirname(prefix))
        return prefix
    # Normalize './out' or 'out'
    norm = prefix.replace("\\", "/")
    if norm.startswith("out/") or norm.startswith("./out/") or norm == "out":
        abs_path = os.path.join(DEFAULT_OUT_DIR, norm.split("out/", 1)[-1])
        ensure_dir(os.path.dirname(abs_path) if os.path.dirname(abs_path) else DEFAULT_OUT_DIR)
        return abs_path
    # If it has a directory component, treat as relative to CWD
    if os.path.dirname(prefix):
        ensure_dir(os.path.dirname(prefix))
        return prefix
    # Bare basename -> under package OUT dir
    ensure_dir(DEFAULT_OUT_DIR)
    return os.path.join(DEFAULT_OUT_DIR, prefix)

def save_json(obj: Any, path: str) -> None:
    if is_dataclass(obj):
        obj = asdict(obj)  # type: ignore
    ensure_dir(os.path.dirname(path) or DEFAULT_OUT_DIR)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
