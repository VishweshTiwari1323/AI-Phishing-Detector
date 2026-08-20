@echo off
echo ============================================
echo AI Phishing Detection System - Setup Wizard
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [1/6] Creating virtual environment...
    python -m venv venv
    echo     ✓ Virtual environment created
) else (
    echo [1/6] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo     ✓ Activated
echo.

REM Install dependencies
echo [3/6] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo     ✗ Installation failed
    pause
    exit /b 1
)
echo     ✓ Dependencies installed
echo.

REM Create .env file
if not exist ".env" (
    echo [4/6] Creating .env configuration file...
    copy .env.example .env >nul
    echo     ✓ .env file created
    echo     ⚠ IMPORTANT: Edit .env and update SECRET_KEY with a random value
) else (
    echo [4/6] .env file already exists
)
echo.

REM Initialize database
echo [5/6] Initializing database...
set FLASK_APP=app.py
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('     ✓ Database initialized')"
if errorlevel 1 (
    echo     ✗ Database initialization failed
    pause
    exit /b 1
)
echo.

REM Seed database
echo [6/6] Creating admin user...
python -c "from app import app, db; from models import User; app.app_context().push(); admin = User.query.filter_by(email='admin@ssipmt.com').first(); import sys; sys.exit(0) if admin else sys.exit(1)" >nul 2>&1
if errorlevel 1 (
    python -c "from app import app, db; from models import User; app.app_context().push(); admin = User(email='admin@ssipmt.com', name='Admin User'); admin.set_password('Admin@123'); db.session.add(admin); db.session.commit(); print('     ✓ Admin user created')"
) else (
    echo     ✓ Admin user already exists
)
echo.

echo ============================================
echo ✓ Setup Complete!
echo ============================================
echo.
echo 📋 Next Steps:
echo    1. Edit .env file and update SECRET_KEY
echo    2. Add your VirusTotal API key to .env
echo    3. Run: python app.py
echo    4. Visit: http://localhost:5000
echo.
echo 🔐 Default Login Credentials:
echo    Email: admin@ssipmt.com
echo    Password: Admin@123
echo    ⚠ CHANGE THESE IMMEDIATELY AFTER LOGIN!
echo.
echo ============================================
pause
