@echo off
setlocal
echo ===================================================
echo     NCAA Volleyball Match Predictor - Windows Setup
echo ===================================================
echo.

set "TARGET_DIR=%~dp0dist"
set "EXE_PATH=%TARGET_DIR%\VolleyballPredictor_Portable.exe"

if not exist "%EXE_PATH%" (
    set "TARGET_DIR=%~dp0dist\VolleyballPredictor"
    set "EXE_PATH=%TARGET_DIR%\VolleyballPredictor.exe"
)

if not exist "%EXE_PATH%" (
    echo [ERROR] Could not find VolleyballPredictor_Portable.exe or VolleyballPredictor.exe in dist\
    echo Please make sure the executable has been built in dist\
    pause
    exit /b 1
)

echo Creating Desktop Shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'NCAA Volleyball Predictor.lnk')); " ^
    "$s.TargetPath = '%EXE_PATH%'; " ^
    "$s.WorkingDirectory = '%TARGET_DIR%'; " ^
    "$s.Description = 'NCAA Volleyball Match Predictor AI/ML'; " ^
    "$s.Save();"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Desktop shortcut 'NCAA Volleyball Predictor' created successfully!
    echo Location: %USERPROFILE%\Desktop\NCAA Volleyball Predictor.lnk
    echo.
    set /p LAUNCH="Do you want to launch the app now? (Y/N): "
    if /i "%LAUNCH%"=="Y" (
        start "" "%EXE_PATH%"
    )
) else (
    echo [ERROR] Failed to create desktop shortcut.
)

endlocal
