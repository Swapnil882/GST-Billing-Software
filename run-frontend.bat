@echo off
title GST Billing Software - Frontend (React + Vite)
echo ========================================================
echo   Starting GST Billing Software - React Frontend (Dev)
echo   Local URL: http://localhost:5173
echo   Proxying API to FastAPI Backend
echo ========================================================
cd /d "%~dp0frontend"
npm run dev
if errorlevel 1 (
    echo.
    echo Frontend dev server stopped with error code %errorlevel%.
    pause
)
