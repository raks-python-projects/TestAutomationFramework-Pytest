@echo off
echo ==========================================
echo   Test Automation Framework Launcher
echo ==========================================

REM Check if .venv exists
IF NOT EXIST ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo [INFO] Virtual environment already exists.
)

REM Activate the virtual environment
echo [INFO] Activating virtual environment...
CALL .venv\Scripts\activate

REM Install dependencies
echo [INFO] Installing dependencies from requrements.txt...
pip install --upgrade pip
pip install -r requirements.txt

REM Run the main application
echo [INFO] Starting the application...
python main.py

echo [INFO] Application finished.
pause