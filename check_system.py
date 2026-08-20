"""
System verification and health check script
"""
import sys
import os

def check_system():
    """Verify all system components"""

    print("🔍 AI Phishing Detection System - Health Check")
    print("=" * 50)

    checks_passed = 0
    total_checks = 0

    # Check 1: Python version
    total_checks += 1
    print("\n[1] Checking Python version...")
    py_version = sys.version_info
    if py_version >= (3, 8):
        print(f"    ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}")
        checks_passed += 1
    else:
        print(f"    ❌ Python {py_version.major}.{py_version.minor} (3.8+ required)")

    # Check 2: Required files
    total_checks += 1
    print("\n[2] Checking required files...")
    required_files = [
        'app.py', 'config.py', 'models.py', 'forms.py',
        'vectorizer.pkl', 'phishing.pkl', 'requirements.txt'
    ]
    all_files_exist = all(os.path.exists(f) for f in required_files)
    if all_files_exist:
        print("    ✅ All required files present")
        checks_passed += 1
    else:
        missing = [f for f in required_files if not os.path.exists(f)]
        print(f"    ❌ Missing files: {', '.join(missing)}")

    # Check 3: Environment file
    total_checks += 1
    print("\n[3] Checking .env configuration...")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            has_vt_key = 'VT_API_KEY=' in env_content and 'your_virustotal' not in env_content
            has_secret = 'SECRET_KEY=' in env_content

            if has_vt_key and has_secret:
                print("    ✅ .env file configured")
                checks_passed += 1
            else:
                print("    ⚠️  .env exists but may need configuration")
                if not has_vt_key:
                    print("       - VT_API_KEY not configured")
                if not has_secret:
                    print("       - SECRET_KEY not configured")
    else:
        print("    ❌ .env file not found")

    # Check 4: Dependencies
    total_checks += 1
    print("\n[4] Checking dependencies...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_wtf
        import flask_limiter
        import flask_caching
        print("    ✅ All Flask extensions installed")
        checks_passed += 1
    except ImportError as e:
        print(f"    ❌ Missing dependency: {e}")

    # Check 5: ML Models
    total_checks += 1
    print("\n[5] Checking ML models...")
    try:
        import pickle
        with open('vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        with open('phishing.pkl', 'rb') as f:
            model = pickle.load(f)
        print("    ✅ ML models loaded successfully")
        checks_passed += 1
    except Exception as e:
        print(f"    ❌ Error loading models: {e}")

    # Check 6: Database
    total_checks += 1
    print("\n[6] Checking database...")
    try:
        from app import app, db
        from models import User

        with app.app_context():
            db.create_all()
            user_count = User.query.count()
            print(f"    ✅ Database accessible ({user_count} users)")
            checks_passed += 1
    except Exception as e:
        print(f"    ❌ Database error: {e}")

    # Check 7: Templates
    total_checks += 1
    print("\n[7] Checking templates...")
    template_files = [
        'templates/index.html',
        'templates/signup.html',
        'templates/scan.html',
        'templates/dashboard.html',
        'templates/history.html',
        'templates/batch_scan.html',
        'templates/error.html'
    ]
    all_templates_exist = all(os.path.exists(f) for f in template_files)
    if all_templates_exist:
        print("    ✅ All templates present")
        checks_passed += 1
    else:
        missing = [f for f in template_files if not os.path.exists(f)]
        print(f"    ⚠️  Missing templates: {', '.join(missing)}")

    # Summary
    print("\n" + "=" * 50)
    print(f"Health Check Summary: {checks_passed}/{total_checks} checks passed")

    if checks_passed == total_checks:
        print("\n🎉 System is ready to run!")
        print("\nStart the application with:")
        print("   python app.py")
        return True
    elif checks_passed >= total_checks - 2:
        print("\n⚠️  System is mostly ready but needs minor configuration")
        return True
    else:
        print("\n❌ System needs attention before running")
        return False

if __name__ == "__main__":
    success = check_system()
    sys.exit(0 if success else 1)
