@echo off
setlocal
cd /d "%~dp0"

set "STARTED=0"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 run_api.py
    if not errorlevel 1 set "STARTED=1"
)

if "%STARTED%"=="0" (
    where python >nul 2>&1
    if not errorlevel 1 (
        python run_api.py
        if not errorlevel 1 set "STARTED=1"
    )
)

if "%STARTED%"=="0" (
    where uv >nul 2>&1
    if not errorlevel 1 (
        uv run --python 3.11 run_api.py
        if not errorlevel 1 set "STARTED=1"
    )
)

if "%STARTED%"=="0" (
    echo.
    echo No se pudo iniciar SecureAPI con py, python o uv.
    echo Verifica instalacion de Python 3.11+ o uv.
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo Error al iniciar SecureAPI.
    pause
)
