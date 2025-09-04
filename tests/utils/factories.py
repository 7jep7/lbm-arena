"""
Model factories for generating test data

This module provides factory functions for creating test instances of all models.
Factories help create consistent, realistic test data with minimal boilerplate.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import json

# Simple fake data generator
def fake_name():
    return f"Test User {random.randint(1, 1000)}"
from app.models.player import Player
from app.models.game import Game, GameType, GameStatus
from app.models.move import Move, GamePlayer


class PlayerFactory:
    """Factory for creating Player test instances"""
    
    @staticmethod
    def create_human_player(
        display_name: str = None,
        elo_chess: int = 1200,  # Match model default
        elo_poker: int = 1200,   # Match model default
        **kwargs
    ) -> Dict[str, Any]:
        """Create a human player data dictionary"""
        return {
            "display_name": display_name if display_name is not None else fake_name(),
            "is_human": True,
            "provider": None,
            "model_id": None,
            "elo_chess": elo_chess,
            "elo_poker": elo_poker,
            **kwargs
        }
    
    @staticmethod
    def create_ai_player(
        display_name: str = "Test AI",
        provider: str = "openai",
        model_id: str = "gpt-4",
        elo_chess: int = 1500,
        elo_poker: int = 1500,
        **kwargs
    ) -> Dict[str, Any]:
        """Create an AI player data dictionary"""
        return {
            "display_name": display_name,
            "is_human": False,
            "provider": provider,
            "model_id": model_id,
            "elo_chess": elo_chess,
            "elo_poker": elo_poker,
            **kwargs
        }
    
    @staticmethod
    def create_multiple_players(count: int = 5) -> List[Dict[str, Any]]:
        """Create multiple diverse players for testing"""
        players = []
        
        # Create a human player
        players.append(PlayerFactory.create_human_player(
            display_name="Human Player",
            elo_chess=random.randint(1200, 2000),
            elo_poker=random.randint(1200, 2000)
        ))
        
        # Create AI players with different providers
        ai_configs = [
            ("GPT-4", "openai", "gpt-4"),
            ("Claude-3", "anthropic", "claude-3-opus"),
            ("GPT-3.5", "openai", "gpt-3.5-turbo"),
            ("Claude-Haiku", "anthropic", "claude-3-haiku")
        ]
        
        for i in range(min(count - 1, len(ai_configs))):
            name, provider, model = ai_configs[i]
            players.append(PlayerFactory.create_ai_player(
                display_name=name,
                provider=provider,
                model_id=model,
                elo_chess=random.randint(1200, 2000),
                elo_poker=random.randint(1200, 2000)
            ))
        
        return players


class GameFactory:
    """Factory for creating Game test instances"""
    
    @staticmethod
    def create_chess_game(
        player_ids: List[int] = None,
        status: GameStatus = GameStatus.WAITING,
        initial_state: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chess game data dictionary"""
        if player_ids is None:
            player_ids = [1, 2]
        
        if initial_state is None:
            initial_state = {
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "turn": "white",
                "castling": "KQkq",
                "en_passant": None,
                "halfmove": 0,
                "fullmove": 1
            }
        
        return {
            "game_type": GameType.CHESS,
            "status": status,
            "initial_state": json.dumps(initial_state),  # Store as JSON string for model
            "current_state": json.dumps(initial_state.copy()),  # Store as JSON string for model
            "player1_id": player_ids[0],  # Required by model
            "player2_id": player_ids[1],  # Required by model
            "player_ids": player_ids,  # For API creation
            **kwargs
        }
    
    @staticmethod
    def create_poker_game(
        player_ids: List[int] = None,
        status: GameStatus = GameStatus.WAITING,
        initial_state: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a poker game data dictionary"""
        if player_ids is None:
            player_ids = [1, 2]
        
        if initial_state is None:
            initial_state = {
                "deck": list(range(52)),  # Simplified deck representation
                "community_cards": [],
                "pot": 0,
                "small_blind": 10,
                "big_blind": 20,
                "dealer": 0,
                "current_player": 1,
                "betting_round": "preflop",
                "players": [
                    {"id": player_ids[0], "chips": 1000, "hole_cards": [], "folded": False},
                    {"id": player_ids[1], "chips": 1000, "hole_cards": [], "folded": False}
                ]
            }
        
        return {
            "game_type": GameType.POKER,
            "status": status,
            "initial_state": json.dumps(initial_state),  # Store as JSON string for model
            "current_state": json.dumps(initial_state.copy()),  # Store as JSON string for model
            "player1_id": player_ids[0],  # Required by model
            "player2_id": player_ids[1] if len(player_ids) > 1 else None,  # Required by model
            "player_ids": player_ids,  # For API creation
            **kwargs
        }
    
    @staticmethod
    def create_in_progress_chess_game(
        player_ids: List[int] = None,
        moves_played: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chess game that's already in progress"""
        game_data = GameFactory.create_chess_game(player_ids, GameStatus.IN_PROGRESS, **kwargs)
        
        # Simulate some moves have been played
        sample_fens = [
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
            "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
            "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"
        ]
        
        if moves_played <= len(sample_fens):
            game_data["current_state"]["fen"] = sample_fens[moves_played - 1]
            game_data["current_state"]["fullmove"] = (moves_played // 2) + 1
        
        return game_data


class MoveFactory:
    """Factory for creating Move test instances"""
    
    @staticmethod
    def create_chess_move(
        game_id: int = 1,
        player_id: int = 1,
        move_number: int = 1,
        move_notation: str = "e4",
        time_taken: int = 5000,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a chess move data dictionary"""
        return {
            "game_id": game_id,
            "player_id": player_id,
            "move_number": move_number,
            "move_data": {
                "from": "e2",
                "to": "e4",
                "piece": "pawn",
                "capture": False,
                "check": False,
                "checkmate": False
            },
            "notation": move_notation,
            "time_taken": time_taken,
            **kwargs
        }
    
    @staticmethod
    def create_poker_move(
        game_id: int = 1,
        player_id: int = 1,
        move_number: int = 1,
        action: str = "call",
        amount: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a poker move data dictionary"""
        return {
            "game_id": game_id,
            "player_id": player_id,
            "move_number": move_number,
            "move_data": {
                "action": action,
                "amount": amount,
                "pot_after": 40,
                "chips_after": 980
            },
            "notation": f"{action}({amount})" if amount > 0 else action,
            "time_taken": random.randint(2000, 10000),
            **kwargs
        }
    
    @staticmethod
    def create_game_sequence(
        game_id: int = 1,
        player_ids: List[int] = None,
        move_count: int = 10
    ) -> List[Dict[str, Any]]:
        """Create a sequence of moves for a game"""
        if player_ids is None:
            player_ids = [1, 2]
        
        moves = []
        for i in range(move_count):
            player_id = player_ids[i % len(player_ids)]
            move = MoveFactory.create_chess_move(
                game_id=game_id,
                player_id=player_id,
                move_number=i + 1,
                move_notation=f"move{i+1}"
            )
            moves.append(move)
        
        return moves


class GamePlayerFactory:
    """Factory for creating GamePlayer test instances"""
    
    @staticmethod
    def create_game_player(
        game_id: int = 1,
        player_id: int = 1,
        position: str = "white",
        elo_before: int = 1500,
        elo_after: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a game player relationship data dictionary"""
        return {
            "game_id": game_id,
            "player_id": player_id,
            "position": position,
            "elo_before": elo_before,
            "elo_after": elo_after,
            **kwargs
        }
    
    @staticmethod
    def create_chess_players(
        game_id: int = 1,
        white_player_id: int = 1,
        black_player_id: int = 2,
        white_elo: int = 1500,
        black_elo: int = 1500
    ) -> List[Dict[str, Any]]:
        """Create both players for a chess game"""
        return [
            GamePlayerFactory.create_game_player(
                game_id=game_id,
                player_id=white_player_id,
                position="white",
                elo_before=white_elo
            ),
            GamePlayerFactory.create_game_player(
                game_id=game_id,
                player_id=black_player_id,
                position="black",
                elo_before=black_elo
            )
        ]


# Convenience functions for quick test data creation

def quick_player_data(name: str = "Test Player", is_ai: bool = False) -> Dict[str, Any]:
    """Quickly create player data for simple tests"""
    if is_ai:
        return PlayerFactory.create_ai_player(display_name=name)
    return PlayerFactory.create_human_player(display_name=name)


def quick_chess_game_data(player_ids: List[int] = None) -> Dict[str, Any]:
    """Quickly create chess game data for simple tests"""
    return GameFactory.create_chess_game(player_ids)


def quick_poker_game_data(player_ids: List[int] = None) -> Dict[str, Any]:
    """Quickly create poker game data for simple tests"""
    return GameFactory.create_poker_game(player_ids)
