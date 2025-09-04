"""
Add test data to the database for frontend testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.player import Player
from app.models.game import Game, GameStatus, GameType

def add_test_data():
    """Add test players and games to the database"""
    db = SessionLocal()
    
    try:
        # Check if we already have test data
        existing_players = db.query(Player).count()
        if existing_players > 0:
            print(f"Database already has {existing_players} players. Skipping test data creation.")
            return
        
        # Create test players
        players = [
            Player(display_name="GPT-4", provider="openai", elo_chess=1500, elo_poker=1500),
            Player(display_name="Claude-3", provider="anthropic", elo_chess=1520, elo_poker=1480),
            Player(display_name="GPT-3.5", provider="openai", elo_chess=1450, elo_poker=1520),
            Player(display_name="Test-Bot", provider="custom", elo_chess=1400, elo_poker=1400),
            Player(display_name="Gemini-Pro", provider="google", elo_chess=1490, elo_poker=1510),
            Player(display_name="LLaMA-2", provider="meta", elo_chess=1470, elo_poker=1460),
        ]
        
        for player in players:
            db.add(player)
        
        db.commit()
        
        # Create test games
        games = [
            Game(
                game_type=GameType.CHESS,
                player1_id=1,
                player2_id=2,
                status=GameStatus.COMPLETED,
                winner_id=1
            ),
            Game(
                game_type=GameType.POKER,
                player1_id=2,
                player2_id=3,
                status=GameStatus.COMPLETED,
                winner_id=2
            ),
            Game(
                game_type=GameType.CHESS,
                player1_id=3,
                player2_id=4,
                status=GameStatus.IN_PROGRESS
            ),
            Game(
                game_type=GameType.CHESS,
                player1_id=5,
                player2_id=6,
                status=GameStatus.COMPLETED,
                winner_id=5
            ),
            Game(
                game_type=GameType.POKER,
                player1_id=1,
                player2_id=6,
                status=GameStatus.IN_PROGRESS
            ),
        ]
        
        for game in games:
            db.add(game)
        
        db.commit()
        
        print("✅ Test data added successfully!")
        print(f"   - Created {len(players)} test players")
        print(f"   - Created {len(games)} test games")
        
    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data()
