@echo off
echo ===================================================
echo   ZSM RECORD - Backend Server
echo ===================================================
echo.
echo Starting Backend API on http://localhost:8001 ...
echo API docs: http://localhost:8001/docs
echo.
echo Keep this window open. Close it to stop the server.
echo ===================================================
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
uvicorn app.main:app --port 8001 --reload
