"""
Add moves and game player data to existing games (simplified version)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.game import Game, GameStatus, GameType
from app.models.player import Player
from app.models.move import Move, GamePlayer
import json

def add_simple_game_data():
    """Add basic moves and game player records"""
    db = SessionLocal()
    
    try:
        # Get existing games and players
        games = db.query(Game).all()
        players = db.query(Player).all()
        
        print(f"Found {len(games)} games and {len(players)} players")
        
        # Add some simple moves for the first completed game
        if games:
            first_game = games[0]
            
            # Add a few chess moves
            if first_game.game_type == GameType.CHESS:
                chess_moves = [
                    {"notation": "e4", "move_data": '{"from": "e2", "to": "e4", "piece": "pawn"}'},
                    {"notation": "e5", "move_data": '{"from": "e7", "to": "e5", "piece": "pawn"}'},
                    {"notation": "Nf3", "move_data": '{"from": "g1", "to": "f3", "piece": "knight"}'},
                ]
                
                for i, move_info in enumerate(chess_moves):
                    player_id = first_game.player1_id if i % 2 == 0 else first_game.player2_id
                    move = Move(
                        game_id=first_game.id,
                        player_id=player_id,
                        move_number=i + 1,
                        move_data=move_info["move_data"],
                        notation=move_info["notation"],
                        time_taken=2000 + (i * 500)
                    )
                    db.add(move)
            
            # Add game player records for the first game
            gp1 = GamePlayer(
                game_id=first_game.id,
                player_id=first_game.player1_id,
                position="white",
                elo_before=1500,
                elo_after=1510
            )
            db.add(gp1)
            
            gp2 = GamePlayer(
                game_id=first_game.id,
                player_id=first_game.player2_id,
                position="black", 
                elo_before=1520,
                elo_after=1510
            )
            db.add(gp2)
        
        db.commit()
        
        # Show results
        total_moves = db.query(Move).count()
        total_game_players = db.query(GamePlayer).count()
        
        print("✅ Successfully added game data!")
        print(f"   - Total moves: {total_moves}")
        print(f"   - Total game players: {total_game_players}")
        
    except Exception as e:
        print(f"❌ Error adding game data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_simple_game_data()
