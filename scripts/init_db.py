#!/usr/bin/env python3
"""
Database initialization script
Drops and recreates all tables with the current schema
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import engine, Base
from backend.models.user import User

def init_database():
    """Drop all tables and recreate them with current schema"""
    print("🗑️  Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("✨ Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized successfully!")
    print("\nNew User table schema includes:")
    print("  - id")
    print("  - username")
    print("  - hashed_password")
    print("  - github_url")
    print("  - github_token")
    print("  - linkedin_id")
    print("  - leetcode_id")
    print("  - gmail")
    print("  - mobile_number")

if __name__ == "__main__":
    init_database()
