.PHONY: run

run:
	@set -e; \
	if command -v python3 >/dev/null 2>&1; then PYTHON="$$(command -v python3)"; \
	elif command -v python >/dev/null 2>&1; then PYTHON="$$(command -v python)"; \
	else echo "Python no encontrado. Instala Python 3.11+ y vuelve a intentar."; exit 1; fi; \
	"$$PYTHON" run_api.py
