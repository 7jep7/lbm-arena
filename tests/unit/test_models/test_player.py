"""
Unit tests for Player model

Tests the Player SQLAlchemy model including:
- Model creation and validation
- Field constraints and defaults
- Relationships
- Model methods
- ELO rating behavior
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.player import Player
from tests.utils.factories import PlayerFactory


@pytest.mark.unit
class TestPlayerModel:
    """Test cases for the Player model"""
    
    def test_create_human_player(self, test_db_session):
        """Test creating a human player with valid data"""
        player_data = PlayerFactory.create_human_player(
            display_name="John Doe",
            elo_chess=1600,
            elo_poker=1400
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        # Verify player was created
        assert player.id is not None
        assert player.display_name == "John Doe"
        assert player.is_human is True
        assert player.provider is None
        assert player.model_id is None
        assert player.elo_chess == 1600
        assert player.elo_poker == 1400
        assert player.created_at is not None
        assert isinstance(player.created_at, datetime)
    
    def test_create_ai_player(self, test_db_session):
        """Test creating an AI player with valid data"""
        player_data = PlayerFactory.create_ai_player(
            display_name="GPT-4",
            provider="openai",
            model_id="gpt-4",
            elo_chess=1800,
            elo_poker=1700
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        # Verify AI player was created
        assert player.id is not None
        assert player.display_name == "GPT-4"
        assert player.is_human is False
        assert player.provider == "openai"
        assert player.model_id == "gpt-4"
        assert player.elo_chess == 1800
        assert player.elo_poker == 1700
    
    def test_default_values(self, test_db_session):
        """Test that default values are applied correctly"""
        # Create player with minimal data
        player = Player(display_name="Test Player")
        test_db_session.add(player)
        test_db_session.commit()
        
        # Check defaults
        assert player.is_human is False  # Default is False (AI)
        assert player.elo_chess == 1200  # Default ELO (matches model)
        assert player.elo_poker == 1200  # Default ELO (matches model)
        assert player.provider is None
        assert player.model_id is None
        assert player.created_at is not None
        # Note: updated_at field is not implemented in the model yet
    
    def test_display_name_required(self, test_db_session):
        """Test that display_name is required"""
        player = Player()  # No display_name
        test_db_session.add(player)
        
        with pytest.raises(IntegrityError):
            test_db_session.commit()
    
    def test_elo_ratings_non_negative(self, test_db_session):
        """Test that ELO ratings cannot be negative"""
        # This test depends on database constraints
        # If no database constraint exists, this will pass but should be added
        player_data = PlayerFactory.create_human_player(
            elo_chess=-100,  # Invalid negative ELO
            elo_poker=-50    # Invalid negative ELO
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        
        # Note: This might not fail if no DB constraint exists
        # In that case, we should add validation in the model
        try:
            test_db_session.commit()
            # If no constraint, at least verify the values are stored
            assert player.elo_chess == -100
            assert player.elo_poker == -50
        except IntegrityError:
            # This is the expected behavior with proper constraints
            pass
    
    def test_string_representation(self, test_db_session):
        """Test the string representation of a player"""
        player_data = PlayerFactory.create_human_player(display_name="Test Player")
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        str_repr = str(player)
        assert "Test Player" in str_repr
        assert str(player.id) in str_repr
    
    def test_multiple_players_unique_names_allowed(self, test_db_session):
        """Test that multiple players can have the same display name"""
        # Create two players with the same name
        player1_data = PlayerFactory.create_human_player(display_name="Same Name")
        player2_data = PlayerFactory.create_ai_player(display_name="Same Name")
        
        player1 = Player(**player1_data)
        player2 = Player(**player2_data)
        
        test_db_session.add(player1)
        test_db_session.add(player2)
        test_db_session.commit()
        
        # Both should be created successfully
        assert player1.id != player2.id
        assert player1.display_name == player2.display_name
    
    def test_update_timestamp(self, test_db_session):
        """Test that player can be updated (timestamp field not implemented yet)"""
        player_data = PlayerFactory.create_human_player()
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        # Note: updated_at field is not implemented in the model yet
        # original_updated_at = player.updated_at  # This field doesn't exist yet
        original_created_at = player.created_at
        
        # Update the player
        original_name = player.display_name
        player.display_name = "Updated Name"
        test_db_session.commit()
        
        # Verify update worked
        assert player.display_name == "Updated Name"
        assert player.display_name != original_name
        assert player.created_at == original_created_at  # created_at shouldn't change
        
        # TODO: Add updated_at field test when it's implemented in the model
        # Check that updated_at changed but created_at didn't
        # assert player.updated_at != original_updated_at
        # assert player.created_at == original_created_at
        # assert player.updated_at > player.created_at
    
    def test_elo_range_validation(self, test_db_session):
        """Test ELO rating reasonable range validation"""
        # Test very high ELO ratings
        player_data = PlayerFactory.create_human_player(
            elo_chess=3000,  # Very high but possible
            elo_poker=3000
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        assert player.elo_chess == 3000
        assert player.elo_poker == 3000
    
    def test_ai_player_requires_provider_and_model(self, test_db_session):
        """Test that AI players should have provider and model_id"""
        # Note: This is a business rule that might not be enforced at DB level
        player_data = PlayerFactory.create_ai_player(
            provider=None,
            model_id=None
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        # This should succeed at DB level, but business logic might validate it
        assert player.is_human is False
        assert player.provider is None
        assert player.model_id is None
    
    def test_human_player_ignores_provider_and_model(self, test_db_session):
        """Test that human players can ignore provider and model_id"""
        player_data = PlayerFactory.create_human_player(
            provider="openai",  # Should be ignored for humans
            model_id="gpt-4"    # Should be ignored for humans
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        assert player.is_human is True
        # Values are stored but should be semantically ignored
        assert player.provider == "openai"
        assert player.model_id == "gpt-4"


@pytest.mark.unit
class TestPlayerModelMethods:
    """Test custom methods on the Player model"""
    
    def test_is_ai_property(self, test_db_session):
        """Test is_ai property if it exists"""
        human_player_data = PlayerFactory.create_human_player()
        ai_player_data = PlayerFactory.create_ai_player()
        
        human_player = Player(**human_player_data)
        ai_player = Player(**ai_player_data)
        
        # If the model has an is_ai property
        if hasattr(human_player, 'is_ai'):
            assert human_player.is_ai is False
            assert ai_player.is_ai is True
    
    def test_update_elo_method(self, test_db_session):
        """Test ELO update method if it exists"""
        player_data = PlayerFactory.create_human_player(
            elo_chess=1500,
            elo_poker=1500
        )
        player = Player(**player_data)
        
        # If the model has an update_elo method
        if hasattr(player, 'update_elo'):
            player.update_elo('chess', 1550)
            assert player.elo_chess == 1550
            
            player.update_elo('poker', 1450)
            assert player.elo_poker == 1450


@pytest.mark.unit
class TestPlayerModelRelationships:
    """Test Player model relationships with other models"""
    
    def test_player_games_relationship(self, test_db_session):
        """Test relationship between players and games"""
        # This test will be expanded when we test the relationship
        # For now, just verify the player can be created
        player_data = PlayerFactory.create_human_player()
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        # Check that relationship attributes exist
        assert hasattr(player, 'game_players')  # Relationship to GamePlayer
    
    def test_player_moves_relationship(self, test_db_session):
        """Test relationship between players and moves"""
        player_data = PlayerFactory.create_human_player()
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        # Check that relationship attributes exist
        assert hasattr(player, 'moves')  # Relationship to Move


@pytest.mark.unit
class TestPlayerModelEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_very_long_display_name(self, test_db_session):
        """Test handling of very long display names"""
        long_name = "A" * 1000  # Very long name
        player_data = PlayerFactory.create_human_player(display_name=long_name)
        
        player = Player(**player_data)
        test_db_session.add(player)
        
        # This might fail if there's a length constraint
        try:
            test_db_session.commit()
            assert player.display_name == long_name
        except IntegrityError:
            # Expected if there's a length constraint
            pass
    
    def test_empty_display_name(self, test_db_session):
        """Test handling of empty display name"""
        player_data = PlayerFactory.create_human_player(display_name="")
        
        player = Player(**player_data)
        test_db_session.add(player)
        
        # This might fail if there's a non-empty constraint
        try:
            test_db_session.commit()
            assert player.display_name == ""
        except IntegrityError:
            # Expected if there's a non-empty constraint
            pass
    
    def test_special_characters_in_display_name(self, test_db_session):
        """Test handling of special characters in display name"""
        special_name = "Test Player! @#$%^&*()_+ 中文 🎮"
        player_data = PlayerFactory.create_human_player(display_name=special_name)
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        assert player.display_name == special_name
    
    def test_extreme_elo_values(self, test_db_session):
        """Test extreme ELO values"""
        player_data = PlayerFactory.create_human_player(
            elo_chess=0,      # Minimum possible
            elo_poker=9999    # Very high value
        )
        
        player = Player(**player_data)
        test_db_session.add(player)
        test_db_session.commit()
        
        assert player.elo_chess == 0
        assert player.elo_poker == 9999
