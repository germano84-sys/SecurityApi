#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Delegate all setup and startup logic to the Python launcher.
if [ -x "${ROOT_DIR}/secureapi/.venv/bin/python" ]; then
	exec "${ROOT_DIR}/secureapi/.venv/bin/python" "${ROOT_DIR}/run_api.py"
elif command -v python3 >/dev/null 2>&1; then
	exec python3 "${ROOT_DIR}/run_api.py"
elif command -v python >/dev/null 2>&1; then
	exec python "${ROOT_DIR}/run_api.py"
else
	echo "No se encontro Python. Instala Python 3.11+ y vuelve a intentar." >&2
	exit 1
fi
