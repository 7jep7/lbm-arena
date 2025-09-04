"""
Complete database setup with proper relationships and rich test data
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

def setup_complete_database():
    """Complete database setup with relationships and test data"""
    
    print("🔨 Creating fresh database with all relationships...")
    
    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create players
        players = [
            Player(display_name="GPT-4", provider="openai", model_id="gpt-4", elo_chess=1500, elo_poker=1500),
            Player(display_name="Claude-3", provider="anthropic", model_id="claude-3-opus", elo_chess=1520, elo_poker=1480),
            Player(display_name="GPT-3.5", provider="openai", model_id="gpt-3.5-turbo", elo_chess=1450, elo_poker=1520),
            Player(display_name="Test-Bot", provider="custom", model_id="test-v1", elo_chess=1400, elo_poker=1400),
            Player(display_name="Gemini-Pro", provider="google", model_id="gemini-pro", elo_chess=1490, elo_poker=1510),
            Player(display_name="LLaMA-2", provider="meta", model_id="llama-2-70b", elo_chess=1470, elo_poker=1460),
        ]
        
        for player in players:
            db.add(player)
        db.commit()
        
        # Refresh to get IDs
        db.refresh(players[0])
        
        # Create games with proper relationships
        games = [
            Game(
                game_type=GameType.CHESS,
                player1_id=players[0].id,
                player2_id=players[1].id,
                status=GameStatus.COMPLETED,
                winner_id=players[0].id,
                initial_state='{"board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
                current_state='{"board": "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 4 3"}'
            ),
            Game(
                game_type=GameType.POKER,
                player1_id=players[1].id,
                player2_id=players[2].id,
                status=GameStatus.COMPLETED,
                winner_id=players[1].id,
                initial_state='{"pot": 0, "blinds": {"small": 5, "big": 10}}',
                current_state='{"pot": 150, "winner": "player1", "final_cards": ["Ah", "Kh", "Qh", "Jh", "Th"]}'
            ),
            Game(
                game_type=GameType.CHESS,
                player1_id=players[2].id,
                player2_id=players[3].id,
                status=GameStatus.IN_PROGRESS,
                initial_state='{"board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
                current_state='{"board": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"}'
            ),
            Game(
                game_type=GameType.CHESS,
                player1_id=players[4].id,
                player2_id=players[5].id,
                status=GameStatus.COMPLETED,
                winner_id=players[4].id,
                initial_state='{"board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
                current_state='{"board": "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"}'
            ),
            Game(
                game_type=GameType.POKER,
                player1_id=players[0].id,
                player2_id=players[5].id,
                status=GameStatus.IN_PROGRESS,
                initial_state='{"pot": 0, "blinds": {"small": 5, "big": 10}}',
                current_state='{"pot": 45, "community": ["Ks", "Qd", "Jc"], "round": "flop"}'
            ),
        ]
        
        for game in games:
            db.add(game)
        db.commit()
        
        # Refresh to get game IDs
        for game in games:
            db.refresh(game)
        
        # Create GamePlayer records (for ELO tracking)
        game_players = []
        for game in games:
            # Player 1
            gp1 = GamePlayer(
                game_id=game.id,
                player_id=game.player1_id,
                position="white" if game.game_type == GameType.CHESS else "player1",
                elo_before=db.query(Player).get(game.player1_id).elo_chess if game.game_type == GameType.CHESS else db.query(Player).get(game.player1_id).elo_poker,
                elo_after=(db.query(Player).get(game.player1_id).elo_chess + (10 if game.winner_id == game.player1_id else -10)) if game.game_type == GameType.CHESS else (db.query(Player).get(game.player1_id).elo_poker + (10 if game.winner_id == game.player1_id else -10))
            )
            game_players.append(gp1)
            
            # Player 2  
            gp2 = GamePlayer(
                game_id=game.id,
                player_id=game.player2_id,
                position="black" if game.game_type == GameType.CHESS else "player2",
                elo_before=db.query(Player).get(game.player2_id).elo_chess if game.game_type == GameType.CHESS else db.query(Player).get(game.player2_id).elo_poker,
                elo_after=(db.query(Player).get(game.player2_id).elo_chess + (10 if game.winner_id == game.player2_id else -10)) if game.game_type == GameType.CHESS else (db.query(Player).get(game.player2_id).elo_poker + (10 if game.winner_id == game.player2_id else -10))
            )
            game_players.append(gp2)
        
        for gp in game_players:
            db.add(gp)
        db.commit()
        
        # Create detailed moves for the completed chess game
        chess_game = games[0]  # First game
        chess_moves = [
            {"notation": "e4", "from": "e2", "to": "e4", "piece": "pawn"},
            {"notation": "e5", "from": "e7", "to": "e5", "piece": "pawn"},
            {"notation": "Nf3", "from": "g1", "to": "f3", "piece": "knight"},
            {"notation": "Nc6", "from": "b8", "to": "c6", "piece": "knight"},
            {"notation": "Bb5", "from": "f1", "to": "b5", "piece": "bishop"},
            {"notation": "a6", "from": "a7", "to": "a6", "piece": "pawn"},
            {"notation": "Ba4", "from": "b5", "to": "a4", "piece": "bishop"},
            {"notation": "Nf6", "from": "g8", "to": "f6", "piece": "knight"},
        ]
        
        moves = []
        for i, move_info in enumerate(chess_moves):
            player_id = chess_game.player1_id if i % 2 == 0 else chess_game.player2_id
            move = Move(
                game_id=chess_game.id,
                player_id=player_id,
                move_number=i + 1,
                move_data=json.dumps({
                    "from": move_info["from"],
                    "to": move_info["to"],
                    "piece": move_info["piece"],
                    "timestamp": f"2024-01-01T10:{10+i}:00Z"
                }),
                notation=move_info["notation"],
                time_taken=2000 + (i * 500) + (i % 3 * 1000)  # Varying think times
            )
            moves.append(move)
        
        # Add moves for the poker game
        poker_game = games[1]  # Second game  
        poker_moves = [
            {"notation": "SB", "action": "small_blind", "amount": 5},
            {"notation": "BB", "action": "big_blind", "amount": 10},
            {"notation": "Call", "action": "call", "amount": 10},
            {"notation": "Check", "action": "check", "amount": 0},
            {"notation": "Bet 20", "action": "bet", "amount": 20},
            {"notation": "Raise 40", "action": "raise", "amount": 40},
            {"notation": "Call", "action": "call", "amount": 40},
            {"notation": "All-in", "action": "all_in", "amount": 75},
        ]
        
        for i, move_info in enumerate(poker_moves):
            player_id = poker_game.player1_id if i % 2 == 0 else poker_game.player2_id
            move = Move(
                game_id=poker_game.id,
                player_id=player_id,
                move_number=i + 1,
                move_data=json.dumps({
                    "action": move_info["action"],
                    "amount": move_info["amount"],
                    "timestamp": f"2024-01-01T11:{10+i}:00Z"
                }),
                notation=move_info["notation"],
                time_taken=1500 + (i * 300)
            )
            moves.append(move)
        
        # Add a few moves for the in-progress chess game
        in_progress_game = games[2]
        early_moves = [
            {"notation": "e4", "from": "e2", "to": "e4", "piece": "pawn"},
            {"notation": "e5", "from": "e7", "to": "e5", "piece": "pawn"},
        ]
        
        for i, move_info in enumerate(early_moves):
            player_id = in_progress_game.player1_id if i % 2 == 0 else in_progress_game.player2_id
            move = Move(
                game_id=in_progress_game.id,
                player_id=player_id,
                move_number=i + 1,
                move_data=json.dumps({
                    "from": move_info["from"],
                    "to": move_info["to"],
                    "piece": move_info["piece"],
                    "timestamp": f"2024-01-01T12:{10+i}:00Z"
                }),
                notation=move_info["notation"],
                time_taken=3000 + (i * 2000)  # Longer think times
            )
            moves.append(move)
        
        # Add all moves
        for move in moves:
            db.add(move)
        db.commit()
        
        # Print summary
        total_players = db.query(Player).count()
        total_games = db.query(Game).count()
        total_moves = db.query(Move).count()
        total_game_players = db.query(GamePlayer).count()
        
        print("✅ Complete database setup successful!")
        print(f"   📊 Players: {total_players}")
        print(f"   🎮 Games: {total_games}")
        print(f"   ♟️  Moves: {total_moves}")
        print(f"   👥 Game Players: {total_game_players}")
        print()
        print("🎯 Database now has rich, interconnected data with:")
        print("   - 6 diverse AI players with different providers")
        print("   - 5 games (3 completed, 2 in progress)")
        print("   - Detailed move histories with timestamps")
        print("   - ELO tracking for both chess and poker")
        print("   - Proper relationships between all entities")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_complete_database()
