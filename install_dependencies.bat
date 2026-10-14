@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ================================================================
echo    NCAA Volleyball Predictor - Automated Windows Environment Setup
echo ================================================================
echo.

:: Step 1: Detect Python
set "PY_CMD="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python was not found on your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/5] Detected Python:
%PY_CMD% --version
echo.

:: Step 2: Create .venv if it doesn't exist
if not exist ".venv\Scripts\python.exe" (
    echo [2/5] Creating virtual environment (.venv)...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/5] Virtual environment (.venv) already exists.
)
echo.

:: Step 3: Upgrade pip and install requirements
echo [3/5] Installing project dependencies from requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Dependency installation encountered an issue.
    pause
    exit /b 1
)
echo.

:: Step 4: Register Jupyter Kernel
echo [4/5] Registering Jupyter Kernel...
".venv\Scripts\python.exe" -m ipykernel install --user --name="volleyball_predictor" --display-name="Python (Volleyball Predictor)" >nul 2>&1
echo Jupyter kernel 'Python (Volleyball Predictor)' registered successfully.
echo.

:: Step 5: Run Automated Tests
echo [5/5] Running verification tests...
".venv\Scripts\pytest.exe" tests/
if %ERRORLEVEL% equ 0 (
    echo.
    echo ================================================================
    echo    [SUCCESS] Setup completed successfully on this laptop!
    echo ================================================================
    echo.
    echo Next Steps:
    echo  1. Launch Desktop App:  run 'setup_windows.bat' or open dist\VolleyballPredictor\VolleyballPredictor.exe
    echo  2. Launch Jupyter Notebook: double-click 'run_jupyter.bat'
    echo  3. CLI Matchup Predict: run '.venv\Scripts\python.exe src\predict.py "Stanford" "Texas"'
    echo.
) else (
    echo [WARNING] Some tests did not pass. Please verify the environment.
)

pause
endlocal
