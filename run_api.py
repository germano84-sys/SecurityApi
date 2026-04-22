#!/usr/bin/env python3
"""Launcher for SecureAPI.

Usage:
    python run_api.py
"""

from pathlib import Path
import subprocess
import sys
import os
from shutil import which


ROOT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = ROOT_DIR / "secureapi" / "requirements.txt"
PROJECT_VENV_DIR = ROOT_DIR / ".venv"
PROJECT_VENV_PYTHON = PROJECT_VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
LEGACY_VENV_CANDIDATES = [
    ROOT_DIR / "secureapi" / ".venv" / "Scripts" / "python.exe",
    ROOT_DIR / "secureapi" / ".venv" / "bin" / "python",
]


def get_python_executable() -> str:
    if PROJECT_VENV_PYTHON.exists():
        return str(PROJECT_VENV_PYTHON)

    for candidate in LEGACY_VENV_CANDIDATES:
        if candidate.exists():
            return str(candidate)

    # Prefer the current interpreter to avoid Windows Store python alias issues.
    return sys.executable


def ensure_project_venv(seed_python: str) -> str:
    if not PROJECT_VENV_PYTHON.exists():
        subprocess.check_call(
            [seed_python, "-m", "venv", str(PROJECT_VENV_DIR)],
            cwd=str(ROOT_DIR),
        )
    return str(PROJECT_VENV_PYTHON)


def ensure_dependencies(python_executable: str) -> str:
    try:
        subprocess.check_call(
            [python_executable, "-c", "import uvicorn"],
            cwd=str(ROOT_DIR),
        )
        return python_executable
    except subprocess.CalledProcessError:
        install_python = python_executable

        # If current interpreter is externally managed (uv/system), install in local .venv.
        if str(PROJECT_VENV_DIR) not in str(Path(python_executable).resolve()):
            install_python = ensure_project_venv(python_executable)

        # Some managed Python distributions create venvs without pip.
        try:
            subprocess.check_call(
                [install_python, "-m", "pip", "--version"],
                cwd=str(ROOT_DIR),
            )
        except subprocess.CalledProcessError:
            subprocess.check_call(
                [install_python, "-m", "ensurepip", "--upgrade"],
                cwd=str(ROOT_DIR),
            )

        try:
            subprocess.check_call(
                [install_python, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
                cwd=str(ROOT_DIR),
            )
        except subprocess.CalledProcessError:
            if not which("uv"):
                raise
            subprocess.check_call(
                ["uv", "pip", "install", "--python", install_python, "-r", str(REQUIREMENTS_FILE)],
                cwd=str(ROOT_DIR),
            )
        return install_python


if __name__ == "__main__":
    python_executable = get_python_executable()
    python_executable = ensure_dependencies(python_executable)

    command = [
        python_executable,
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
