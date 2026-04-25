#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filesystem helpers for regulatorTool.

The helpers in this module resolve package-local input and output paths and
write JSON payloads for reports. The docstrings avoid reStructuredText lists so
that Sphinx autodoc can parse the module safely.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_IN_DIR = os.path.join(PKG_DIR, "in")
DEFAULT_OUT_DIR = os.path.join(PKG_DIR, "out")


def ensure_dir(d: str) -> None:
    """Create a directory when it does not already exist."""
    os.makedirs(d, exist_ok=True)


def out_path(*parts: str, out_dir: str | None = None) -> str:
    """Build a path under the regulatorTool output directory."""
    d = DEFAULT_OUT_DIR if out_dir is None else out_dir
    ensure_dir(d)
    return os.path.join(d, *parts)


def resolve_save_prefix(prefix: str | None) -> str | None:
    """Resolve a save prefix to a path that can receive file suffixes.

    A missing prefix returns None. Absolute paths are returned after ensuring
    their parent directory exists. Prefixes beginning with out are resolved
    under the package output directory. Bare basenames are also placed under the
    package output directory. Other relative paths are resolved relative to the
    current working directory after ensuring their parent directory exists.
    """
    if not prefix:
        return None
    if os.path.isabs(prefix):
        ensure_dir(os.path.dirname(prefix))
        return prefix

    norm = prefix.replace("\\", "/")
    if norm.startswith("out/") or norm.startswith("./out/") or norm == "out":
        abs_path = os.path.join(DEFAULT_OUT_DIR, norm.split("out/", 1)[-1])
        ensure_dir(os.path.dirname(abs_path) if os.path.dirname(abs_path) else DEFAULT_OUT_DIR)
        return abs_path

    if os.path.dirname(prefix):
        ensure_dir(os.path.dirname(prefix))
        return prefix

    ensure_dir(DEFAULT_OUT_DIR)
    return os.path.join(DEFAULT_OUT_DIR, prefix)


def save_json(obj: Any, path: str) -> None:
    """Write an object as formatted JSON."""
    if is_dataclass(obj):
        obj = asdict(obj)  # type: ignore[arg-type]
    ensure_dir(os.path.dirname(path) or DEFAULT_OUT_DIR)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
