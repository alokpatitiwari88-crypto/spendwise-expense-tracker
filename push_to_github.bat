@echo off
setlocal enabledelayedexpansion
title Push SpendWise to GitHub
echo ============================================================
echo           SpendWise - Push to GitHub Helper
echo ============================================================
echo.
echo Make sure you have created an empty repository on GitHub:
echo   1. Visit https://github.com/new
echo   2. Name your repo (e.g., "expense-tracker")
echo   3. Set it to "Public"
echo   4. Do NOT initialize with README, .gitignore or license
echo   5. Click "Create repository"
echo.
echo ------------------------------------------------------------
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/expense-tracker.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL entered. Exiting.
    pause
    exit /b 1
)

echo.
echo Linking repository to: %REPO_URL%
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Pushing code to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Your project has been uploaded to GitHub!
    echo.
    echo Copy this link for your Internship Google Form:
    echo %REPO_URL%
    echo ============================================================
) else (
    echo.
    echo [NOTE] If prompted, please sign in via the browser window.
)

echo.
pause
