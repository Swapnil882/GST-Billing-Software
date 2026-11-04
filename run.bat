@echo off
title Free GST Billing Software - Live Server Logs
echo Starting GST Billing Software (FastAPI + React)...
python "%~dp0run.py" %*
if errorlevel 1 (
    echo.
    echo Server process exited with code %errorlevel%.
    pause
)
