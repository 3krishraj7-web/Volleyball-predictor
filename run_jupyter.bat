@echo off
setlocal
cd /d "%~dp0"

echo =======================================================
echo    Launching Volleyball Predictor in Jupyter Notebook
echo =======================================================
echo.

if not exist ".venv\Scripts\jupyter.exe" (
    echo [ERROR] Jupyter environment not found in .venv.
    echo Please run install_dependencies.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting Jupyter server...
start "" ".venv\Scripts\jupyter.exe" notebook "notebooks\volleyball_predictor.ipynb"

endlocal
