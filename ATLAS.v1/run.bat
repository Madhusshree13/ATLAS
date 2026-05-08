@echo off
title Atlas
cd /d "%~dp0"
echo Starting Atlas...
venv\Scripts\python.exe main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Atlas exited with an error. See above for details.
    pause
)
