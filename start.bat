@echo off
echo ==============================================
echo        A-Share Terminal Startup Script
echo ==============================================

echo Activating Python environment...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

echo Installing backend requirements...
pip install -r requirements.txt

echo Starting Backend Server...
python run.py

pause
