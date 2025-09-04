"""
Safe database initialization script for production deployments
- Creates database tables if they don't exist
- Never adds test data (production should start empty)
- Never drops or modifies existing data
- Safe to run on every deployment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.player import Player
from app.models.game import Game, GameStatus, GameType
from app.models.move import Move, GamePlayer
import json

def init_database_safely():
    """Initialize database tables only - no test data for production"""
    
    try:
        # Check if we can connect to the database
        with engine.connect() as conn:
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    try:
        # Create tables if they don't exist (this is safe - won't drop existing tables)
        print("🔧 Ensuring database tables exist...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified/created")
        
        # Check current database state
        db = SessionLocal()
        try:
            player_count = db.query(Player).count()
            game_count = db.query(Game).count()
            move_count = db.query(Move).count()
            
            print(f"📊 Current database state:")
            print(f"   - Players: {player_count}")
            print(f"   - Games: {game_count}")
            print(f"   - Moves: {move_count}")
            
            if player_count == 0 and game_count == 0:
                print("✅ Database is ready for production use (empty)")
            else:
                print("✅ Database has existing data - preserving all data")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        return False

if __name__ == "__main__":
    success = init_database_safely()
    if not success:
        sys.exit(1)
    print("🎯 Database initialization completed - ready for production use!")
