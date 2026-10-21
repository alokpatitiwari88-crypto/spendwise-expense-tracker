@echo off
setlocal
title SpendWise - Expense Tracker
echo =======================================================
echo          SpendWise Expense Tracker Starting...
echo =======================================================
echo.

:: Detect Python executable (checking Anaconda path and PATH)
set "PY_CMD="
if exist "%USERPROFILE%\anaconda3\python.exe" (
    set "PY_CMD=%USERPROFILE%\anaconda3\python.exe"
) else if exist "C:\ProgramData\anaconda3\python.exe" (
    set "PY_CMD=C:\ProgramData\anaconda3\python.exe"
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python was not found on your system!
    echo Please ensure Python or Anaconda is installed.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Using Python: %PY_CMD%
echo.
echo Starting Flask web application...
echo -------------------------------------------------------
echo   Dashboard URL: http://127.0.0.1:5000
echo -------------------------------------------------------
echo Press Ctrl+C in this terminal window to stop the server.
echo.

"%PY_CMD%" app.py
pause
