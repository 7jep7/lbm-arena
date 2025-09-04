"""
Unit tests for Game model

Tests the Game SQLAlchemy model including:
- Model creation and validation
- Game type and status validation
- State management (initial_state, current_state)
- Relationships with players and moves
- Game lifecycle methods
"""

import pytest
import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.game import Game, GameType, GameStatus
from app.models.player import Player
from tests.utils.factories import GameFactory, PlayerFactory
from tests.utils.helpers import create_test_players


@pytest.mark.unit
class TestGameModel:
    """Test cases for the Game model"""
    
    def test_create_chess_game(self, test_db_session):
        """Test creating a chess game with valid data"""
        game_data = GameFactory.create_chess_game()
        # Remove player_ids as it's not a direct field
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Verify game was created
        assert game.id is not None
        assert game.game_type == GameType.CHESS
        assert game.status == GameStatus.WAITING
        assert game.initial_state is not None
        assert game.current_state is not None
        assert game.created_at is not None
        assert isinstance(game.created_at, datetime)
        assert game.winner_id is None
    
    def test_create_poker_game(self, test_db_session):
        """Test creating a poker game with valid data"""
        game_data = GameFactory.create_poker_game()
        # Remove player_ids as it's not a direct field
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Verify game was created
        assert game.id is not None
        assert game.game_type == GameType.POKER
        assert game.status == GameStatus.WAITING
        assert game.initial_state is not None
        assert game.current_state is not None
        assert "community_cards" in game.initial_state
        assert "pot" in game.initial_state
    
    def test_game_type_enum_validation(self, test_db_session):
        """Test that game_type must be a valid GameType"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        
        # Valid game type
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        assert game.game_type == GameType.CHESS
        
        # Test that enum validation works
        assert GameType.CHESS.value == "chess"
        assert GameType.POKER.value == "poker"
    
    def test_game_status_enum_validation(self, test_db_session):
        """Test that status must be a valid GameStatus"""
        game_data = GameFactory.create_chess_game(status=GameStatus.IN_PROGRESS)
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        assert game.status == GameStatus.IN_PROGRESS
        
        # Test all valid statuses
        assert GameStatus.WAITING.value == "waiting"
        assert GameStatus.IN_PROGRESS.value == "in_progress"
        assert GameStatus.COMPLETED.value == "completed"
        assert GameStatus.ABORTED.value == "aborted"
    
    def test_game_state_json_serialization(self, test_db_session):
        """Test that game states are properly stored as JSON"""
        initial_state = {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "turn": "white",
            "castling": "KQkq"
        }
        
        current_state = {
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "turn": "black",
            "castling": "KQkq"
        }
        
        game_data = GameFactory.create_chess_game(
            initial_state=initial_state,
            current_state=current_state
        )
        game_data.pop('player_ids', None)
        game_data['current_state'] = current_state
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Retrieve and verify JSON serialization worked
        retrieved_game = test_db_session.query(Game).filter_by(id=game.id).first()
        assert retrieved_game.initial_state == initial_state
        assert retrieved_game.current_state == current_state
        assert retrieved_game.initial_state["fen"] == initial_state["fen"]
    
    def test_game_with_winner(self, test_db_session):
        """Test creating a completed game with a winner"""
        # Create players first
        players = create_test_players(test_db_session, 2)
        
        game_data = GameFactory.create_chess_game(
            status=GameStatus.COMPLETED,
            player_ids=[players[0].id, players[1].id]
        )
        game_data.pop('player_ids', None)
        game_data['winner_id'] = players[0].id
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        assert game.status == GameStatus.COMPLETED
        assert game.winner_id == players[0].id
    
    def test_game_without_winner(self, test_db_session):
        """Test that games can exist without a winner"""
        game_data = GameFactory.create_chess_game(status=GameStatus.WAITING)
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        assert game.winner_id is None
    
    def test_update_timestamp(self, test_db_session):
        """Test that updated_at is set when game is modified"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        original_updated_at = game.updated_at
        original_created_at = game.created_at
        
        # Update the game
        game.status = GameStatus.IN_PROGRESS
        test_db_session.commit()
        
        # Check that updated_at changed but created_at didn't
        assert game.updated_at != original_updated_at
        assert game.created_at == original_created_at
        if game.updated_at and original_created_at:
            assert game.updated_at > original_created_at
    
    def test_string_representation(self, test_db_session):
        """Test the string representation of a game"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        str_repr = str(game)
        assert "chess" in str_repr.lower()
        assert str(game.id) in str_repr


@pytest.mark.unit
class TestGameModelStateMutation:
    """Test game state modification methods"""
    
    def test_update_current_state(self, test_db_session):
        """Test updating the current game state"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Update current state
        new_state = {
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "turn": "black"
        }
        game.current_state = new_state
        test_db_session.commit()
        
        # Verify state was updated
        assert game.current_state == new_state
        assert game.initial_state != new_state  # Initial state unchanged
    
    def test_game_progression_states(self, test_db_session):
        """Test typical game status progression"""
        game_data = GameFactory.create_chess_game(status=GameStatus.WAITING)
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Progression: WAITING -> IN_PROGRESS -> COMPLETED
        assert game.status == GameStatus.WAITING
        
        game.status = GameStatus.IN_PROGRESS
        test_db_session.commit()
        assert game.status == GameStatus.IN_PROGRESS
        
        game.status = GameStatus.COMPLETED
        test_db_session.commit()
        assert game.status == GameStatus.COMPLETED


@pytest.mark.unit
class TestGameModelRelationships:
    """Test Game model relationships with other models"""
    
    def test_game_players_relationship(self, test_db_session):
        """Test relationship between games and game_players"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Check that relationship attributes exist
        assert hasattr(game, 'game_players')  # Relationship to GamePlayer
        assert hasattr(game, 'moves')         # Relationship to Move
    
    def test_winner_relationship(self, test_db_session):
        """Test relationship to winner player"""
        # Create a player to be the winner
        players = create_test_players(test_db_session, 1)
        winner = players[0]
        
        game_data = GameFactory.create_chess_game(status=GameStatus.COMPLETED)
        game_data.pop('player_ids', None)
        game_data['winner_id'] = winner.id
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Check winner relationship
        assert game.winner_id == winner.id
        if hasattr(game, 'winner'):
            assert game.winner.id == winner.id


@pytest.mark.unit
class TestGameModelEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_game_state(self, test_db_session):
        """Test handling of empty game states"""
        game_data = GameFactory.create_chess_game(
            initial_state={},
            current_state={}
        )
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        assert game.initial_state == {}
        assert game.current_state == {}
    
    def test_large_game_state(self, test_db_session):
        """Test handling of large game states"""
        # Create a large state object
        large_state = {
            "data": ["item_" + str(i) for i in range(1000)],
            "metadata": {"key_" + str(i): "value_" + str(i) for i in range(100)}
        }
        
        game_data = GameFactory.create_chess_game(
            initial_state=large_state,
            current_state=large_state.copy()
        )
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Verify large state was stored correctly
        retrieved_game = test_db_session.query(Game).filter_by(id=game.id).first()
        assert len(retrieved_game.initial_state["data"]) == 1000
        assert len(retrieved_game.initial_state["metadata"]) == 100
    
    def test_invalid_winner_id(self, test_db_session):
        """Test handling of invalid winner_id"""
        game_data = GameFactory.create_chess_game(status=GameStatus.COMPLETED)
        game_data.pop('player_ids', None)
        game_data['winner_id'] = 99999  # Non-existent player ID
        
        game = Game(**game_data)
        test_db_session.add(game)
        
        # This might fail with foreign key constraint
        try:
            test_db_session.commit()
            assert game.winner_id == 99999
        except IntegrityError:
            # Expected if there's a foreign key constraint
            pass
    
    def test_null_game_states(self, test_db_session):
        """Test handling of null game states"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        game_data['initial_state'] = None
        game_data['current_state'] = None
        
        game = Game(**game_data)
        test_db_session.add(game)
        
        # This might fail if states are required
        try:
            test_db_session.commit()
            assert game.initial_state is None
            assert game.current_state is None
        except IntegrityError:
            # Expected if states are required
            pass


@pytest.mark.unit
class TestGameModelValidation:
    """Test validation logic in the Game model"""
    
    def test_chess_game_initial_state_structure(self, test_db_session):
        """Test that chess games have proper initial state structure"""
        game_data = GameFactory.create_chess_game()
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Check chess-specific fields in initial state
        initial_state = game.initial_state
        assert "fen" in initial_state
        assert "turn" in initial_state
        assert initial_state["fen"].startswith("rnbqkbnr")  # Starting position
    
    def test_poker_game_initial_state_structure(self, test_db_session):
        """Test that poker games have proper initial state structure"""
        game_data = GameFactory.create_poker_game()
        game_data.pop('player_ids', None)
        
        game = Game(**game_data)
        test_db_session.add(game)
        test_db_session.commit()
        
        # Check poker-specific fields in initial state
        initial_state = game.initial_state
        assert "community_cards" in initial_state
        assert "pot" in initial_state
        assert "players" in initial_state
        assert isinstance(initial_state["community_cards"], list)
        assert isinstance(initial_state["pot"], int)
    
    def test_game_type_consistency(self, test_db_session):
        """Test that game type matches state structure"""
        # Chess game with chess state
        chess_data = GameFactory.create_chess_game()
        chess_data.pop('player_ids', None)
        
        chess_game = Game(**chess_data)
        test_db_session.add(chess_game)
        test_db_session.commit()
        
        assert chess_game.game_type == GameType.CHESS
        assert "fen" in chess_game.initial_state
        
        # Poker game with poker state
        poker_data = GameFactory.create_poker_game()
        poker_data.pop('player_ids', None)
        
        poker_game = Game(**poker_data)
        test_db_session.add(poker_game)
        test_db_session.commit()
        
        assert poker_game.game_type == GameType.POKER
        assert "community_cards" in poker_game.initial_state
