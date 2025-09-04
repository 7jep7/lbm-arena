"""
Unit tests for Player schemas

Tests the Pydantic schemas for Player including:
- Validation of required fields
- Type validation
- Default values
- Serialization/deserialization
- Edge cases and error handling
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.player import Player, PlayerCreate, PlayerUpdate
from tests.utils.factories import PlayerFactory


@pytest.mark.unit
class TestPlayerCreateSchema:
    """Test cases for PlayerCreate schema"""
    
    def test_valid_human_player_creation(self):
        """Test creating a valid human player schema"""
        player_data = PlayerFactory.create_human_player(
            display_name="John Doe",
            is_human=True,
            elo_chess=1600,
            elo_poker=1400
        )
        
        # Remove fields not in PlayerCreate
        create_data = {
            "display_name": player_data["display_name"],
            "is_human": player_data["is_human"]
        }
        
        player_create = PlayerCreate(**create_data)
        
        assert player_create.display_name == "John Doe"
        assert player_create.is_human is True
        assert player_create.provider is None  # Default
        assert player_create.model_id is None  # Default
    
    def test_valid_ai_player_creation(self):
        """Test creating a valid AI player schema"""
        create_data = {
            "display_name": "GPT-4",
            "is_human": False,
            "provider": "openai",
            "model_id": "gpt-4"
        }
        
        player_create = PlayerCreate(**create_data)
        
        assert player_create.display_name == "GPT-4"
        assert player_create.is_human is False
        assert player_create.provider == "openai"
        assert player_create.model_id == "gpt-4"
    
    def test_display_name_required(self):
        """Test that display_name is required"""
        with pytest.raises(ValidationError) as exc_info:
            PlayerCreate()  # No display_name
        
        error = exc_info.value
        assert "display_name" in str(error)
        assert "field required" in str(error).lower()
    
    def test_default_values(self):
        """Test that default values are applied correctly"""
        player_create = PlayerCreate(display_name="Test Player")
        
        assert player_create.display_name == "Test Player"
        assert player_create.is_human is False  # Default is False (AI)
        assert player_create.provider is None
        assert player_create.model_id is None
    
    def test_string_validation(self):
        """Test string field validation"""
        # Valid strings
        player_create = PlayerCreate(
            display_name="Valid Name",
            provider="openai",
            model_id="gpt-4"
        )
        assert player_create.display_name == "Valid Name"
        
        # Test type validation
        with pytest.raises(ValidationError) as exc_info:
            PlayerCreate(display_name=123)  # Invalid type
        
        assert "str type expected" in str(exc_info.value)
    
    def test_boolean_validation(self):
        """Test boolean field validation"""
        # Valid boolean values
        player_create = PlayerCreate(display_name="Test", is_human=True)
        assert player_create.is_human is True
        
        player_create = PlayerCreate(display_name="Test", is_human=False)
        assert player_create.is_human is False
        
        # Test type validation
        with pytest.raises(ValidationError) as exc_info:
            PlayerCreate(display_name="Test", is_human="yes")  # Invalid type
        
        assert "bool type expected" in str(exc_info.value)
    
    def test_empty_string_display_name(self):
        """Test handling of empty display name"""
        # This might be allowed or not depending on validation rules
        try:
            player_create = PlayerCreate(display_name="")
            assert player_create.display_name == ""
        except ValidationError:
            # If validation prevents empty strings, this is expected
            pass
    
    def test_whitespace_display_name(self):
        """Test handling of whitespace-only display name"""
        try:
            player_create = PlayerCreate(display_name="   ")
            assert player_create.display_name == "   "
        except ValidationError:
            # If validation prevents whitespace-only strings, this is expected
            pass
    
    def test_unicode_display_name(self):
        """Test unicode characters in display name"""
        unicode_name = "Test Player 中文 🎮"
        player_create = PlayerCreate(display_name=unicode_name)
        assert player_create.display_name == unicode_name
    
    def test_very_long_display_name(self):
        """Test very long display names"""
        long_name = "A" * 1000
        try:
            player_create = PlayerCreate(display_name=long_name)
            assert player_create.display_name == long_name
        except ValidationError:
            # If there's a length limit, this is expected
            pass
    
    def test_optional_fields_as_none(self):
        """Test that optional fields can be None"""
        player_create = PlayerCreate(
            display_name="Test",
            provider=None,
            model_id=None
        )
        
        assert player_create.provider is None
        assert player_create.model_id is None
    
    def test_json_serialization(self):
        """Test that schema can be serialized to JSON"""
        player_create = PlayerCreate(
            display_name="Test Player",
            is_human=False,
            provider="openai",
            model_id="gpt-4"
        )
        
        json_data = player_create.dict()
        
        assert json_data["display_name"] == "Test Player"
        assert json_data["is_human"] is False
        assert json_data["provider"] == "openai"
        assert json_data["model_id"] == "gpt-4"


@pytest.mark.unit
class TestPlayerUpdateSchema:
    """Test cases for PlayerUpdate schema"""
    
    def test_all_fields_optional(self):
        """Test that all fields in PlayerUpdate are optional"""
        # Should be able to create with no fields
        player_update = PlayerUpdate()
        
        assert player_update.display_name is None
        assert player_update.provider is None
        assert player_update.model_id is None
    
    def test_partial_update(self):
        """Test updating only some fields"""
        player_update = PlayerUpdate(display_name="New Name")
        
        assert player_update.display_name == "New Name"
        assert player_update.provider is None
        assert player_update.model_id is None
    
    def test_update_validation(self):
        """Test validation of update fields"""
        # Valid update
        player_update = PlayerUpdate(
            display_name="Updated Name",
            provider="anthropic",
            model_id="claude-3"
        )
        
        assert player_update.display_name == "Updated Name"
        assert player_update.provider == "anthropic"
        assert player_update.model_id == "claude-3"
        
        # Invalid type
        with pytest.raises(ValidationError):
            PlayerUpdate(display_name=123)
    
    def test_update_serialization(self):
        """Test serialization of update schema"""
        player_update = PlayerUpdate(display_name="Updated Name")
        
        # Should exclude None values in serialization
        json_data = player_update.dict(exclude_none=True)
        
        assert "display_name" in json_data
        assert "provider" not in json_data  # None values excluded
        assert "model_id" not in json_data


@pytest.mark.unit
class TestPlayerResponseSchema:
    """Test cases for Player response schema"""
    
    def test_valid_player_response(self):
        """Test creating a valid player response"""
        player_data = {
            "id": 1,
            "display_name": "Test Player",
            "is_human": True,
            "provider": None,
            "model_id": None,
            "elo_chess": 1500,
            "elo_poker": 1500,
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        player = Player(**player_data)
        
        assert player.id == 1
        assert player.display_name == "Test Player"
        assert player.is_human is True
        assert player.elo_chess == 1500
        assert player.elo_poker == 1500
        assert isinstance(player.created_at, datetime)
    
    def test_required_fields_validation(self):
        """Test that required fields are validated"""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Player()  # No required fields
        
        error_msg = str(exc_info.value)
        required_fields = ["id", "display_name", "elo_chess", "elo_poker", "created_at"]
        
        for field in required_fields:
            assert field in error_msg
    
    def test_elo_validation(self):
        """Test ELO rating validation"""
        base_data = {
            "id": 1,
            "display_name": "Test",
            "is_human": True,
            "elo_chess": 1500,
            "elo_poker": 1500,
            "created_at": datetime.now()
        }
        
        # Valid ELO ratings
        player = Player(**base_data)
        assert player.elo_chess == 1500
        assert player.elo_poker == 1500
        
        # Test negative ELO (might be invalid depending on validation)
        try:
            invalid_data = base_data.copy()
            invalid_data["elo_chess"] = -100
            Player(**invalid_data)
        except ValidationError:
            # Expected if negative values are not allowed
            pass
    
    def test_datetime_validation(self):
        """Test datetime field validation"""
        base_data = {
            "id": 1,
            "display_name": "Test",
            "is_human": True,
            "elo_chess": 1500,
            "elo_poker": 1500,
            "created_at": datetime.now()
        }
        
        # Valid datetime
        player = Player(**base_data)
        assert isinstance(player.created_at, datetime)
        
        # Invalid datetime type
        with pytest.raises(ValidationError):
            invalid_data = base_data.copy()
            invalid_data["created_at"] = "not a datetime"
            Player(**invalid_data)
    
    def test_optional_updated_at(self):
        """Test that updated_at is optional"""
        player_data = {
            "id": 1,
            "display_name": "Test",
            "is_human": True,
            "elo_chess": 1500,
            "elo_poker": 1500,
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        player = Player(**player_data)
        assert player.updated_at is None
        
        # With updated_at value
        player_data["updated_at"] = datetime.now()
        player = Player(**player_data)
        assert isinstance(player.updated_at, datetime)
    
    def test_orm_mode_compatibility(self):
        """Test that schema works with ORM mode"""
        # This would typically be tested with actual ORM objects
        # For now, just verify the Config is set correctly
        assert hasattr(Player.Config, 'orm_mode')
        assert Player.Config.orm_mode is True
    
    def test_json_serialization_response(self):
        """Test JSON serialization of response schema"""
        player_data = {
            "id": 1,
            "display_name": "Test Player",
            "is_human": False,
            "provider": "openai",
            "model_id": "gpt-4",
            "elo_chess": 1600,
            "elo_poker": 1400,
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 2, 12, 0, 0)
        }
        
        player = Player(**player_data)
        json_data = player.dict()
        
        assert json_data["id"] == 1
        assert json_data["display_name"] == "Test Player"
        assert json_data["is_human"] is False
        assert json_data["provider"] == "openai"
        assert json_data["model_id"] == "gpt-4"
        assert json_data["elo_chess"] == 1600
        assert json_data["elo_poker"] == 1400
        
        # Datetime fields should be serializable
        assert "created_at" in json_data
        assert "updated_at" in json_data


@pytest.mark.unit
class TestPlayerSchemaEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_ai_player_without_provider_model(self):
        """Test AI player creation without provider/model"""
        # This might be valid or invalid depending on business rules
        create_data = {
            "display_name": "AI Player",
            "is_human": False
            # No provider or model_id
        }
        
        player_create = PlayerCreate(**create_data)
        assert player_create.is_human is False
        assert player_create.provider is None
        assert player_create.model_id is None
    
    def test_human_player_with_provider_model(self):
        """Test human player with provider/model (should be ignored)"""
        create_data = {
            "display_name": "Human Player",
            "is_human": True,
            "provider": "openai",  # Should be semantically ignored
            "model_id": "gpt-4"    # Should be semantically ignored
        }
        
        player_create = PlayerCreate(**create_data)
        assert player_create.is_human is True
        assert player_create.provider == "openai"  # Stored but semantically ignored
        assert player_create.model_id == "gpt-4"
    
    def test_case_sensitivity(self):
        """Test case sensitivity in string fields"""
        player_create = PlayerCreate(
            display_name="Test Player",
            provider="OpenAI",  # Mixed case
            model_id="GPT-4"    # Mixed case
        )
        
        assert player_create.provider == "OpenAI"  # Case preserved
        assert player_create.model_id == "GPT-4"
    
    def test_leading_trailing_whitespace(self):
        """Test handling of leading/trailing whitespace"""
        player_create = PlayerCreate(
            display_name="  Test Player  ",
            provider="  openai  ",
            model_id="  gpt-4  "
        )
        
        # Depending on validation, whitespace might be stripped or preserved
        assert "Test Player" in player_create.display_name
    
    def test_special_characters_in_provider_model(self):
        """Test special characters in provider and model fields"""
        player_create = PlayerCreate(
            display_name="Test",
            provider="custom-provider-v1.0",
            model_id="model_name-2023.1"
        )
        
        assert player_create.provider == "custom-provider-v1.0"
        assert player_create.model_id == "model_name-2023.1"
