"""Database initialization and verification script."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def init_database():
    """Initialize the database and create tables."""
    try:
        from app import app, db
        from models import ScanHistory, User

        with app.app_context():
            print("🗄️  Initializing database...")

            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")

            # Check if admin user exists
            admin = User.query.filter_by(email="admin@ssipmt.com").first()

            if not admin:
                print("\n👤 Creating admin user...")
                admin = User(email="admin@ssipmt.com", name="Admin User")
                admin.set_password("Admin@123")
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created successfully")
                print("\n🔐 Default Credentials:")
                print("   Email: admin@ssipmt.com")
                print("   Password: Admin@123")
                print("   ⚠️  CHANGE THESE IMMEDIATELY AFTER FIRST LOGIN!")
            else:
                print("✅ Admin user already exists")

            # Verify tables
            print("\n📊 Database Status:")
            print(f"   Users: {User.query.count()}")
            print(f"   Scan History: {ScanHistory.query.count()}")

            print("\n✅ Database initialization complete!")
            return True

    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)