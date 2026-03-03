@echo off
echo ==============================================
echo        A-Share Terminal Build ^& Run Script
echo ==============================================

echo [1/3] Setting up Backend Environment...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo [2/3] Building Frontend UI...
cd frontend
call npm install
call npm run build
cd ..

echo [3/3] Copying Frontend Assets to Backend Static Folder...
xcopy /E /I /Y frontend\dist\* backend\static\

echo Starting Backend Server...
cd backend
python run.py

pause
