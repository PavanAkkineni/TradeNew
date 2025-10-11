"""
Initialize the database for TradeCompass
Run this script to create all database tables
"""
from app.database import init_db

if __name__ == "__main__":
    print("Initializing TradeCompass database...")
    init_db()
    print("✅ Database initialized successfully!")
    print("\nYou can now:")
    print("1. Start the server: python run_app.py")
    print("2. Open http://localhost:8000 in your browser")
    print("3. Create an account via the signup page")
