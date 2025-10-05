#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
io.py — filesystem helpers for regulatorTool.
"""

from __future__ import annotations
import os, json
from dataclasses import asdict, is_dataclass
from typing import Any

DEFAULT_IN_DIR  = os.path.join("stateSpaceDesign", "regulatorTool", "in")
DEFAULT_OUT_DIR = os.path.join("stateSpaceDesign", "regulatorTool", "out")

def ensure_dir(d: str) -> None:
    os.makedirs(d, exist_ok=True)

def out_path(*parts: str, out_dir: str | None = None) -> str:
    d = DEFAULT_OUT_DIR if out_dir is None else out_dir
    ensure_dir(d)
    return os.path.join(d, *parts)

def save_json(obj: Any, path: str) -> None:
    if is_dataclass(obj):
        obj = asdict(obj)  # type: ignore
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
