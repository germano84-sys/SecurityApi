#!/usr/bin/env python3
"""Minimal launcher that delegates execution to secureapi/main.py.

Usage:
    python run_api.py
"""

from pathlib import Path
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parent
MAIN_FILE = ROOT_DIR / "secureapi" / "main.py"
VENV_PYTHON = ROOT_DIR / "secureapi" / ".venv" / "bin" / "python"


def get_python_executable():
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


if __name__ == "__main__":
    raise SystemExit(subprocess.call([get_python_executable(), str(MAIN_FILE)]))
