"""
Add 2 more players to the existing database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.player import Player

def add_two_more_players():
    """Add 2 more players to the existing database"""
    db = SessionLocal()
    
    try:
        # Add 2 new players
        new_players = [
            Player(display_name="Gemini-Pro", provider="google", elo_chess=1490, elo_poker=1510),
            Player(display_name="LLaMA-2", provider="meta", elo_chess=1470, elo_poker=1460),
        ]
        
        for player in new_players:
            db.add(player)
        
        db.commit()
        
        print("✅ Added 2 more players successfully!")
        print(f"   - Gemini-Pro (Google)")
        print(f"   - LLaMA-2 (Meta)")
        
        # Show total count
        total_players = db.query(Player).count()
        print(f"   - Total players in database: {total_players}")
        
    except Exception as e:
        print(f"❌ Error adding players: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_two_more_players()
