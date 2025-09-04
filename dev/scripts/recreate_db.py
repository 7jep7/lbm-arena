"""
Drop all tables and recreate them fresh
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import engine, Base
from app.models import player, game, move

def drop_and_create_tables():
    """Drop all existing tables and create fresh ones"""
    try:
        print("🗑️  Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        print("🔨 Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables recreated successfully!")
        
    except Exception as e:
        print(f"❌ Error recreating tables: {e}")

if __name__ == "__main__":
    drop_and_create_tables()
