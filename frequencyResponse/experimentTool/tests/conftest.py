import os
import sys
from pathlib import Path
import pytest

# Use non-interactive backend for matplotlib
os.environ.setdefault("MPLBACKEND", "Agg")

@pytest.fixture(scope="session")
def repo_root() -> Path:
    # Assume tests are executed from repo root (as in your current setup)
    return Path(__file__).resolve().parents[3]

@pytest.fixture
def out_dir(repo_root: Path) -> Path:
    p = repo_root / "frequencyResponse" / "experimentTool" / "out"
    p.mkdir(parents=True, exist_ok=True)
    return p
