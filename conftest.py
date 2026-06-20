"""Pytest configuration."""

import sys
from pathlib import Path

repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))

core_path = repo_root.parent / "pyfarm-core" / "src"
if core_path.exists():
    sys.path.insert(0, str(core_path))
