@echo off
REM Batch script to build the Automation Builder executable
REM This script installs PyInstaller if needed and builds the .exe

echo ========================================
echo Automation Builder - EXE Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Installing/Updating PyInstaller...
python -m pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Building executable...
echo This may take a few minutes...
echo.

python build_exe.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your executable is located at: dist\AutomationBuilder.exe
echo.
echo You can now distribute this .exe file to other Windows computers
echo without requiring Python to be installed.
echo.
pause
