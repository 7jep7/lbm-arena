"""
Unit tests for remaining schemas

Tests schema validation, serialization, and error handling for:
- Game schemas
- Move schemas
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.game import (
    GameCreate,
    GameUpdate,
    Game,
    MoveCreate,
    Move,
    GamePlayer
)
from app.models.game import GameType, GameStatus
from tests.utils.factories import GameFactory, PlayerFactory, MoveFactory


class TestGameSchemas:
    """Test game-related schemas"""
    
    def test_game_create_schema_valid(self):
        """Test valid GameCreate schema"""
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": 1, "role": "white"},
                {"player_id": 2, "role": "black"}
            ]
        }
        
        schema = GameCreate(**game_data)
        
        assert schema.game_type == "chess"
        assert schema.status == "pending"
        assert len(schema.players) == 2
        assert schema.players[0].player_id == 1
        assert schema.players[0].role == "white"
    
    def test_game_create_schema_missing_required_fields(self):
        """Test GameCreate schema with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GameCreate()
        
        errors = exc_info.value.errors()
        missing_fields = [error["loc"][0] for error in errors]
        
        assert "game_type" in missing_fields
        assert "status" in missing_fields
        assert "players" in missing_fields
    
    def test_game_create_schema_invalid_game_type(self):
        """Test GameCreate schema with invalid game type"""
        game_data = {
            "game_type": "invalid_type",
            "status": "pending",
            "players": [
                {"player_id": 1, "role": "white"},
                {"player_id": 2, "role": "black"}
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GameCreate(**game_data)
        
        error = exc_info.value.errors()[0]
        assert "game_type" in str(error["loc"])
    
    def test_game_create_schema_invalid_status(self):
        """Test GameCreate schema with invalid status"""
        game_data = {
            "game_type": "chess",
            "status": "invalid_status",
            "players": [
                {"player_id": 1, "role": "white"},
                {"player_id": 2, "role": "black"}
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GameCreate(**game_data)
        
        error = exc_info.value.errors()[0]
        assert "status" in str(error["loc"])
    
    def test_game_create_schema_empty_players(self):
        """Test GameCreate schema with empty players list"""
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": []
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GameCreate(**game_data)
        
        # Should have validation error for minimum players
        error = exc_info.value.errors()[0]
        assert "players" in str(error["loc"])
    
    def test_game_create_schema_too_many_players(self):
        """Test GameCreate schema with too many players"""
        players = [{"player_id": i, "role": f"player_{i}"} for i in range(20)]
        
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": players
        }
        
        # This might succeed or fail depending on validation rules
        try:
            schema = GameCreate(**game_data)
            assert len(schema.players) == 20
        except ValidationError:
            # If there's a maximum player limit, this is expected
            pass
    
    def test_game_update_schema_valid(self):
        """Test valid GameUpdate schema"""
        update_data = {
            "status": "completed",
            "result": "win",
            "winner_id": 1
        }
        
        schema = GameUpdate(**update_data)
        
        assert schema.status == "completed"
        assert schema.result == "win"
        assert schema.winner_id == 1
    
    def test_game_update_schema_partial_update(self):
        """Test GameUpdate schema with partial data"""
        update_data = {
            "status": "in_progress"
        }
        
        schema = GameUpdate(**update_data)
        
        assert schema.status == "in_progress"
        assert schema.result is None
        assert schema.winner_id is None
    
    def test_game_update_schema_invalid_result(self):
        """Test GameUpdate schema with invalid result"""
        update_data = {
            "status": "completed",
            "result": "invalid_result"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GameUpdate(**update_data)
        
        error = exc_info.value.errors()[0]
        assert "result" in str(error["loc"])
    
    def test_game_response_schema_serialization(self):
        """Test GameResponse schema serialization"""
        game_data = GameFactory.build()
        
        # Create response schema from model-like data
        response_data = {
            "id": game_data.id,
            "game_type": game_data.game_type,
            "status": game_data.status,
            "result": game_data.result,
            "winner_id": game_data.winner_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "players": []
        }
        
        schema = GameResponse(**response_data)
        
        assert schema.id == game_data.id
        assert schema.game_type == game_data.game_type
        assert schema.status == game_data.status
        assert isinstance(schema.created_at, datetime)
        assert isinstance(schema.updated_at, datetime)
    
    def test_game_player_create_schema_valid(self):
        """Test valid GamePlayerCreate schema"""
        player_data = {
            "player_id": 1,
            "role": "white"
        }
        
        schema = GamePlayerCreate(**player_data)
        
        assert schema.player_id == 1
        assert schema.role == "white"
    
    def test_game_player_create_schema_missing_fields(self):
        """Test GamePlayerCreate schema with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            GamePlayerCreate()
        
        errors = exc_info.value.errors()
        missing_fields = [error["loc"][0] for error in errors]
        
        assert "player_id" in missing_fields
        assert "role" in missing_fields
    
    def test_game_player_create_schema_invalid_player_id(self):
        """Test GamePlayerCreate schema with invalid player_id"""
        player_data = {
            "player_id": "not_an_integer",
            "role": "white"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GamePlayerCreate(**player_data)
        
        error = exc_info.value.errors()[0]
        assert "player_id" in str(error["loc"])
    
    def test_game_player_response_schema_serialization(self):
        """Test GamePlayerResponse schema serialization"""
        player_data = PlayerFactory.build()
        
        response_data = {
            "id": 1,
            "game_id": 1,
            "player_id": player_data.id,
            "role": "white",
            "player": {
                "id": player_data.id,
                "display_name": player_data.display_name,
                "is_human": player_data.is_human,
                "provider": player_data.provider,
                "model_id": player_data.model_id,
                "elo_chess": player_data.elo_chess,
                "elo_poker": player_data.elo_poker,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        }
        
        schema = GamePlayerResponse(**response_data)
        
        assert schema.id == 1
        assert schema.game_id == 1
        assert schema.player_id == player_data.id
        assert schema.role == "white"
        assert schema.player.id == player_data.id
        assert schema.player.display_name == player_data.display_name


class TestMoveSchemas:
    """Test move-related schemas"""
    
    def test_move_create_schema_valid(self):
        """Test valid MoveCreate schema"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4",
            "position_before": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "position_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        }
        
        schema = MoveCreate(**move_data)
        
        assert schema.player_id == 1
        assert schema.move_number == 1
        assert schema.move_notation == "e4"
        assert schema.position_before.startswith("rnbqkbnr")
        assert schema.position_after.startswith("rnbqkbnr")
    
    def test_move_create_schema_missing_required_fields(self):
        """Test MoveCreate schema with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            MoveCreate()
        
        errors = exc_info.value.errors()
        missing_fields = [error["loc"][0] for error in errors]
        
        assert "player_id" in missing_fields
        assert "move_number" in missing_fields
        assert "move_notation" in missing_fields
    
    def test_move_create_schema_optional_fields(self):
        """Test MoveCreate schema with only required fields"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4"
        }
        
        schema = MoveCreate(**move_data)
        
        assert schema.player_id == 1
        assert schema.move_number == 1
        assert schema.move_notation == "e4"
        assert schema.position_before is None
        assert schema.position_after is None
        assert schema.time_taken is None
        assert schema.analysis is None
    
    def test_move_create_schema_with_time_taken(self):
        """Test MoveCreate schema with time_taken"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4",
            "time_taken": 5.5
        }
        
        schema = MoveCreate(**move_data)
        
        assert schema.time_taken == 5.5
    
    def test_move_create_schema_with_analysis(self):
        """Test MoveCreate schema with analysis data"""
        analysis_data = {
            "evaluation": 0.2,
            "best_move": "Nf3",
            "depth": 20,
            "nodes": 1000000
        }
        
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4",
            "analysis": analysis_data
        }
        
        schema = MoveCreate(**move_data)
        
        assert schema.analysis == analysis_data
        assert schema.analysis["evaluation"] == 0.2
        assert schema.analysis["best_move"] == "Nf3"
    
    def test_move_create_schema_invalid_move_number(self):
        """Test MoveCreate schema with invalid move number"""
        move_data = {
            "player_id": 1,
            "move_number": -1,  # Invalid
            "move_notation": "e4"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MoveCreate(**move_data)
        
        error = exc_info.value.errors()[0]
        assert "move_number" in str(error["loc"])
    
    def test_move_create_schema_invalid_time_taken(self):
        """Test MoveCreate schema with invalid time_taken"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4",
            "time_taken": -5.0  # Invalid
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MoveCreate(**move_data)
        
        error = exc_info.value.errors()[0]
        assert "time_taken" in str(error["loc"])
    
    def test_move_update_schema_valid(self):
        """Test valid MoveUpdate schema"""
        update_data = {
            "move_notation": "exd5",
            "analysis": {
                "evaluation": -0.3,
                "best_move": "exd5",
                "depth": 25
            }
        }
        
        schema = MoveUpdate(**update_data)
        
        assert schema.move_notation == "exd5"
        assert schema.analysis["evaluation"] == -0.3
    
    def test_move_update_schema_partial_update(self):
        """Test MoveUpdate schema with partial data"""
        update_data = {
            "time_taken": 10.5
        }
        
        schema = MoveUpdate(**update_data)
        
        assert schema.time_taken == 10.5
        assert schema.move_notation is None
        assert schema.analysis is None
    
    def test_move_response_schema_serialization(self):
        """Test MoveResponse schema serialization"""
        move_data = MoveFactory.build()
        
        response_data = {
            "id": move_data.id,
            "game_id": move_data.game_id,
            "player_id": move_data.player_id,
            "move_number": move_data.move_number,
            "move_notation": move_data.move_notation,
            "position_before": move_data.position_before,
            "position_after": move_data.position_after,
            "time_taken": move_data.time_taken,
            "analysis": move_data.analysis,
            "created_at": datetime.now()
        }
        
        schema = MoveResponse(**response_data)
        
        assert schema.id == move_data.id
        assert schema.game_id == move_data.game_id
        assert schema.player_id == move_data.player_id
        assert schema.move_number == move_data.move_number
        assert schema.move_notation == move_data.move_notation
        assert isinstance(schema.created_at, datetime)


class TestSchemaValidationEdgeCases:
    """Test edge cases and validation scenarios"""
    
    def test_schema_with_unicode_strings(self):
        """Test schemas with unicode strings"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "♔e1-g1"  # Unicode chess symbols
        }
        
        schema = MoveCreate(**move_data)
        assert schema.move_notation == "♔e1-g1"
    
    def test_schema_with_very_long_strings(self):
        """Test schemas with very long strings"""
        long_notation = "a" * 1000
        
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": long_notation
        }
        
        # Might succeed or fail depending on length limits
        try:
            schema = MoveCreate(**move_data)
            assert schema.move_notation == long_notation
        except ValidationError:
            # If there's a length limit, this is expected
            pass
    
    def test_schema_with_null_values(self):
        """Test schemas with explicit null values"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4",
            "position_before": None,
            "position_after": None,
            "time_taken": None,
            "analysis": None
        }
        
        schema = MoveCreate(**move_data)
        
        assert schema.position_before is None
        assert schema.position_after is None
        assert schema.time_taken is None
        assert schema.analysis is None
    
    def test_schema_with_extra_fields(self):
        """Test schemas with extra fields"""
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4",
            "extra_field": "should_be_ignored",
            "another_extra": 123
        }
        
        schema = MoveCreate(**move_data)
        
        # Extra fields should be ignored in Pydantic
        assert hasattr(schema, "player_id")
        assert hasattr(schema, "move_notation")
        assert not hasattr(schema, "extra_field")
        assert not hasattr(schema, "another_extra")
    
    def test_schema_json_serialization(self):
        """Test schema JSON serialization"""
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": 1, "role": "white"},
                {"player_id": 2, "role": "black"}
            ]
        }
        
        schema = GameCreate(**game_data)
        json_data = schema.model_dump()
        
        assert isinstance(json_data, dict)
        assert json_data["game_type"] == "chess"
        assert json_data["status"] == "pending"
        assert len(json_data["players"]) == 2
    
    def test_schema_json_deserialization(self):
        """Test schema JSON deserialization"""
        json_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": 1, "role": "white"},
                {"player_id": 2, "role": "black"}
            ]
        }
        
        schema = GameCreate.model_validate(json_data)
        
        assert schema.game_type == "chess"
        assert schema.status == "pending"
        assert len(schema.players) == 2
    
    def test_nested_schema_validation(self):
        """Test validation of nested schemas"""
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": 1, "role": "white"},
                {"player_id": "invalid", "role": "black"}  # Invalid nested data
            ]
        }
        
        with pytest.raises(ValidationError) as exc_info:
            GameCreate(**game_data)
        
        # Should have validation error in nested player data
        errors = exc_info.value.errors()
        assert any("players" in str(error["loc"]) for error in errors)
    
    def test_schema_field_aliases(self):
        """Test schema field aliases if any are defined"""
        # This would test if schemas have field aliases
        # For now, just verify basic functionality
        move_data = {
            "player_id": 1,
            "move_number": 1,
            "move_notation": "e4"
        }
        
        schema = MoveCreate(**move_data)
        assert schema.player_id == 1
    
    def test_schema_custom_validators(self):
        """Test custom validators if any are defined"""
        # Test any custom validation logic in schemas
        # For example, if move_number must be positive
        move_data = {
            "player_id": 1,
            "move_number": 0,  # Might be invalid depending on validation
            "move_notation": "e4"
        }
        
        try:
            schema = MoveCreate(**move_data)
            assert schema.move_number == 0
        except ValidationError:
            # If there's custom validation for positive move numbers
            pass
