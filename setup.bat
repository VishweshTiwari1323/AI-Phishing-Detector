@echo off
echo Setting up AI Phishing Detection System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo Python found
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env file and add your VirusTotal API key and secret key
)

REM Initialize database
echo Initializing database...
flask init-db

REM Seed database
echo Creating admin user...
flask seed-db

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your VirusTotal API key
echo 2. Update SECRET_KEY in .env with a strong random key
echo 3. Run the application with: flask run
echo 4. Or for development: python app.py
echo.
echo Default admin credentials:
echo    Email: admin@ssipmt.com
echo    Password: Admin@123
echo    Change these credentials after first login!
echo.

pause
