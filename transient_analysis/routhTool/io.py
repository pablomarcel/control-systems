# transient_analysis/routhTool/io.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Dict

@dataclass(slots=True)
class RouthPaths:
    root: Path
    in_dir: Path
    out_dir: Path

    @classmethod
    def from_package_root(cls, package_root: Path) -> "RouthPaths":
        base = package_root
        return cls(
            root=base,
            in_dir=base / "in",
            out_dir=base / "out",
        )

def ensure_dirs(paths: RouthPaths):
    paths.in_dir.mkdir(parents=True, exist_ok=True)
    paths.out_dir.mkdir(parents=True, exist_ok=True)

def write_text(out_path: Path, text: str, *, encoding="utf-8") -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding=encoding)
    return out_path

def dump_json(out_path: Path, obj: Dict[str, Any], *, encoding="utf-8") -> Path:
    import json
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, indent=2), encoding=encoding)
    return out_path