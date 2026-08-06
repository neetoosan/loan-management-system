"""
Initialize the database and create default admin credentials.

Run this script after deleting the database to set up a fresh one:
    python app/init_admin.py
"""
import sys
import os

# Add app directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from database.connection import init_db, create_user, get_all_users


def setup():
    """Initialize database and create admin account."""
    # 1. Initialize database (creates all tables)
    print("=" * 50)
    print("  Morning Star Cooperative - Database Setup")
    print("=" * 50)
    init_db()

    # 2. Check if admin already exists
    users = get_all_users()
    admin_exists = any(u.username == "admin" for u in users)

    if admin_exists:
        print("\n[!] Admin account already exists. Skipping creation.")
    else:
        # 3. Create default admin account
        try:
            create_user(
                username="admin",
                email="admin@morningstar.coop",
                password="admin123",
                full_name="Administrator",
                role="ADMIN",
            )
            print("\n[OK] Admin account created successfully!")
            print("-" * 50)
            print("  Username : admin")
            print("  Password : admin123")
            print("  Role     : Admin")
            print("-" * 50)
            print("\n  ⚠  Change the password after first login!")
        except Exception as e:
            print(f"\n[ERROR] Failed to create admin: {e}")
            return

    print("\n[OK] Database is ready. You can now run the app.")
    print("     python app/app.py")


if __name__ == "__main__":
    setup()
