@echo off
title GST Billing Software - FastAPI Backend Server
echo ========================================================
echo   Starting GST Billing Software - FastAPI Backend
echo   Environment: Python 3.11 / FastAPI / PostgreSQL
echo ========================================================
python "%~dp0backend\run.py" %*
if errorlevel 1 (
    echo.
    echo Backend server stopped with error code %errorlevel%.
    pause
)
