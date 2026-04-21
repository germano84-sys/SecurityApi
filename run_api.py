#!/usr/bin/env python3
"""Launcher for SecureAPI.

Usage:
    python run_api.py
"""

from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = ROOT_DIR / "secureapi" / ".venv" / "bin" / "python"


def get_python_executable() -> str:
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


if __name__ == "__main__":
    command = [
        get_python_executable(),
        "-m",
        "uvicorn",
        "secureapi.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8007",
        "--reload",
    ]

    try:
        raise SystemExit(subprocess.call(command, cwd=str(ROOT_DIR)))
    except KeyboardInterrupt:
        raise SystemExit(0)
