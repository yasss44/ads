@echo off
echo Setting up Flask Location Manager...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=True
set DATABASE_URL=sqlite:///dev.db
set SECRET_KEY=dev-secret-key

REM Remove old database if it exists (for schema updates)
if exist "dev.db" (
    echo Removing old database for schema update...
    del "dev.db"
)

REM Create database tables with new schema
echo Setting up database with enhanced features...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created with enhanced schema!')"

REM Create demo users if they don't exist
echo Creating demo users...
python create_demo_users.py

REM Create sample data if it doesn't exist
echo Creating sample data...
python create_sample_data.py

REM Start Flask development server
echo Starting Flask development server...
echo.
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
