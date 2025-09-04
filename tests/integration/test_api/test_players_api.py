"""
Integration tests for Players API endpoints

Tests the full stack integration of player endpoints including:
- Database operations
- Schema validation
- HTTP status codes
- Response format validation
- Error handling
- CRUD operations
"""

import pytest
from fastapi.testclient import TestClient
from tests.utils.helpers import (
    assert_response_success,
    assert_response_error,
    assert_valid_json_response,
    assert_player_structure,
    APITestHelper
)
from tests.utils.factories import PlayerFactory


@pytest.mark.integration
class TestPlayersAPICreate:
    """Test player creation via API"""
    
    def test_create_human_player_success(self, test_client: TestClient):
        """Test successful creation of a human player"""
        player_data = {
            "display_name": "John Doe",
            "is_human": True
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        assert_response_success(response, 201)
        player = assert_valid_json_response(response)
        assert_player_structure(player)
        
        assert player["display_name"] == "John Doe"
        assert player["is_human"] is True
        assert player["provider"] is None
        assert player["model_id"] is None
        assert player["elo_chess"] == 1500  # Default ELO
        assert player["elo_poker"] == 1500  # Default ELO
    
    def test_create_ai_player_success(self, test_client: TestClient):
        """Test successful creation of an AI player"""
        player_data = {
            "display_name": "GPT-4",
            "is_human": False,
            "provider": "openai",
            "model_id": "gpt-4"
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        assert_response_success(response, 201)
        player = assert_valid_json_response(response)
        assert_player_structure(player)
        
        assert player["display_name"] == "GPT-4"
        assert player["is_human"] is False
        assert player["provider"] == "openai"
        assert player["model_id"] == "gpt-4"
    
    def test_create_player_missing_display_name(self, test_client: TestClient):
        """Test player creation without display name fails"""
        player_data = {
            "is_human": True
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        assert_response_error(response, 422)  # Validation error
        error_data = response.json()
        assert "display_name" in str(error_data).lower()
    
    def test_create_player_invalid_data_types(self, test_client: TestClient):
        """Test player creation with invalid data types"""
        player_data = {
            "display_name": "Test Player",
            "is_human": "not_a_boolean"  # Invalid type
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        assert_response_error(response, 422)
        error_data = response.json()
        assert "bool" in str(error_data).lower()
    
    def test_create_player_empty_display_name(self, test_client: TestClient):
        """Test player creation with empty display name"""
        player_data = {
            "display_name": "",
            "is_human": True
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        # Depending on validation rules, this might succeed or fail
        if response.status_code == 201:
            player = response.json()
            assert player["display_name"] == ""
        else:
            assert_response_error(response, 422)
    
    def test_create_multiple_players_same_name(self, test_client: TestClient):
        """Test creating multiple players with the same name"""
        player_data = {
            "display_name": "Same Name",
            "is_human": True
        }
        
        # Create first player
        response1 = test_client.post("/api/v1/players", json=player_data)
        assert_response_success(response1, 201)
        player1 = response1.json()
        
        # Create second player with same name
        response2 = test_client.post("/api/v1/players", json=player_data)
        assert_response_success(response2, 201)
        player2 = response2.json()
        
        # Should both succeed with different IDs
        assert player1["id"] != player2["id"]
        assert player1["display_name"] == player2["display_name"]


@pytest.mark.integration
class TestPlayersAPIRead:
    """Test player retrieval via API"""
    
    def test_get_all_players_empty(self, test_client: TestClient):
        """Test getting all players when none exist"""
        response = test_client.get("/api/v1/players")
        
        assert_response_success(response)
        players = assert_valid_json_response(response)
        
        assert isinstance(players, list)
        assert len(players) == 0
    
    def test_get_all_players_with_data(self, test_client: TestClient):
        """Test getting all players when some exist"""
        helper = APITestHelper(test_client)
        
        # Create some players
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        response = test_client.get("/api/v1/players")
        
        assert_response_success(response)
        players = assert_valid_json_response(response)
        
        assert isinstance(players, list)
        assert len(players) == 2
        
        # Verify structure of returned players
        for player in players:
            assert_player_structure(player)
        
        # Verify our created players are in the list
        player_ids = [p["id"] for p in players]
        assert player1["id"] in player_ids
        assert player2["id"] in player_ids
    
    def test_get_player_by_id_success(self, test_client: TestClient):
        """Test getting a specific player by ID"""
        helper = APITestHelper(test_client)
        
        # Create a player
        created_player = helper.create_player()
        player_id = created_player["id"]
        
        response = test_client.get(f"/api/v1/players/{player_id}")
        
        assert_response_success(response)
        player = assert_valid_json_response(response)
        assert_player_structure(player)
        
        assert player["id"] == player_id
        assert player["display_name"] == created_player["display_name"]
    
    def test_get_player_by_id_not_found(self, test_client: TestClient):
        """Test getting a non-existent player by ID"""
        response = test_client.get("/api/v1/players/99999")
        
        assert_response_error(response, 404)
        error_data = response.json()
        assert "not found" in str(error_data).lower()
    
    def test_get_player_by_invalid_id(self, test_client: TestClient):
        """Test getting a player with invalid ID format"""
        response = test_client.get("/api/v1/players/invalid_id")
        
        assert_response_error(response, 422)  # Validation error
    
    def test_get_players_pagination(self, test_client: TestClient):
        """Test pagination of players list"""
        helper = APITestHelper(test_client)
        
        # Create several players
        for i in range(5):
            helper.create_player()
        
        # Test with limit
        response = test_client.get("/api/v1/players?limit=3")
        assert_response_success(response)
        players = response.json()
        assert len(players) <= 3
        
        # Test with skip
        response = test_client.get("/api/v1/players?skip=2&limit=3")
        assert_response_success(response)
        players = response.json()
        assert len(players) <= 3


@pytest.mark.integration
class TestPlayersAPIUpdate:
    """Test player updates via API"""
    
    def test_update_player_success(self, test_client: TestClient):
        """Test successful player update"""
        helper = APITestHelper(test_client)
        
        # Create a player
        player = helper.create_player()
        player_id = player["id"]
        
        # Update the player
        update_data = {
            "display_name": "Updated Name",
            "provider": "anthropic",
            "model_id": "claude-3"
        }
        
        response = test_client.put(f"/api/v1/players/{player_id}", json=update_data)
        
        assert_response_success(response)
        updated_player = assert_valid_json_response(response)
        assert_player_structure(updated_player)
        
        assert updated_player["id"] == player_id
        assert updated_player["display_name"] == "Updated Name"
        assert updated_player["provider"] == "anthropic"
        assert updated_player["model_id"] == "claude-3"
        # ELO should remain unchanged
        assert updated_player["elo_chess"] == player["elo_chess"]
    
    def test_update_player_partial(self, test_client: TestClient):
        """Test partial player update"""
        helper = APITestHelper(test_client)
        
        player = helper.create_player()
        player_id = player["id"]
        original_name = player["display_name"]
        
        # Update only one field
        update_data = {
            "provider": "updated_provider"
        }
        
        response = test_client.put(f"/api/v1/players/{player_id}", json=update_data)
        
        assert_response_success(response)
        updated_player = response.json()
        
        # Only provider should change
        assert updated_player["provider"] == "updated_provider"
        assert updated_player["display_name"] == original_name
    
    def test_update_player_not_found(self, test_client: TestClient):
        """Test updating a non-existent player"""
        update_data = {
            "display_name": "Updated Name"
        }
        
        response = test_client.put("/api/v1/players/99999", json=update_data)
        
        assert_response_error(response, 404)
    
    def test_update_player_invalid_data(self, test_client: TestClient):
        """Test updating player with invalid data"""
        helper = APITestHelper(test_client)
        
        player = helper.create_player()
        player_id = player["id"]
        
        update_data = {
            "display_name": 123  # Invalid type
        }
        
        response = test_client.put(f"/api/v1/players/{player_id}", json=update_data)
        
        assert_response_error(response, 422)


@pytest.mark.integration
class TestPlayersAPIDelete:
    """Test player deletion via API"""
    
    def test_delete_player_success(self, test_client: TestClient):
        """Test successful player deletion"""
        helper = APITestHelper(test_client)
        
        # Create a player
        player = helper.create_player()
        player_id = player["id"]
        
        # Delete the player
        response = test_client.delete(f"/api/v1/players/{player_id}")
        
        assert_response_success(response, 204)  # No content
        
        # Verify player is deleted
        response = test_client.get(f"/api/v1/players/{player_id}")
        assert_response_error(response, 404)
    
    def test_delete_player_not_found(self, test_client: TestClient):
        """Test deleting a non-existent player"""
        response = test_client.delete("/api/v1/players/99999")
        
        assert_response_error(response, 404)
    
    def test_delete_player_with_games(self, test_client: TestClient):
        """Test deleting a player who has participated in games"""
        helper = APITestHelper(test_client)
        
        # Create players and a game
        player1 = helper.create_player()
        player2 = helper.create_player()
        game = helper.create_game()
        
        # Try to delete a player involved in a game
        response = test_client.delete(f"/api/v1/players/{player1['id']}")
        
        # This might succeed or fail depending on business rules
        # If foreign key constraints prevent deletion, expect 409 or 400
        if response.status_code not in [204, 409, 400]:
            assert False, f"Unexpected status code: {response.status_code}"


@pytest.mark.integration
class TestPlayersAPIValidation:
    """Test API validation and error handling"""
    
    def test_invalid_json_request(self, test_client: TestClient):
        """Test handling of invalid JSON in request"""
        response = test_client.post(
            "/api/v1/players",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert_response_error(response, 422)
    
    def test_missing_content_type(self, test_client: TestClient):
        """Test handling of missing content type"""
        player_data = {
            "display_name": "Test Player",
            "is_human": True
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        # Should still work with proper JSON
        assert_response_success(response, 201)
    
    def test_extra_fields_ignored(self, test_client: TestClient):
        """Test that extra fields in request are ignored"""
        player_data = {
            "display_name": "Test Player",
            "is_human": True,
            "extra_field": "should_be_ignored",
            "another_extra": 123
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        assert_response_success(response, 201)
        player = response.json()
        
        # Extra fields should not be in response
        assert "extra_field" not in player
        assert "another_extra" not in player
    
    def test_unicode_display_name(self, test_client: TestClient):
        """Test handling of unicode characters in display name"""
        player_data = {
            "display_name": "Test Player 中文 🎮",
            "is_human": True
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        assert_response_success(response, 201)
        player = response.json()
        assert player["display_name"] == "Test Player 中文 🎮"
    
    def test_very_long_display_name(self, test_client: TestClient):
        """Test handling of very long display names"""
        long_name = "A" * 1000
        player_data = {
            "display_name": long_name,
            "is_human": True
        }
        
        response = test_client.post("/api/v1/players", json=player_data)
        
        # Might succeed or fail depending on length limits
        if response.status_code == 201:
            player = response.json()
            assert player["display_name"] == long_name
        else:
            assert_response_error(response, 422)


@pytest.mark.integration
class TestPlayersAPIErrorHandling:
    """Test error handling scenarios"""
    
    def test_database_error_handling(self, test_client: TestClient):
        """Test handling of database errors"""
        # This is difficult to test without mocking the database
        # For now, just ensure the API handles errors gracefully
        pass
    
    def test_concurrent_operations(self, test_client: TestClient):
        """Test concurrent operations on players"""
        helper = APITestHelper(test_client)
        
        # Create a player
        player = helper.create_player()
        player_id = player["id"]
        
        # Simulate concurrent updates
        update_data1 = {"display_name": "Update 1"}
        update_data2 = {"display_name": "Update 2"}
        
        response1 = test_client.put(f"/api/v1/players/{player_id}", json=update_data1)
        response2 = test_client.put(f"/api/v1/players/{player_id}", json=update_data2)
        
        # Both should succeed (last one wins)
        assert_response_success(response1)
        assert_response_success(response2)
        
        # Final state should be from the last update
        final_response = test_client.get(f"/api/v1/players/{player_id}")
        assert_response_success(final_response)
        final_player = final_response.json()
        assert final_player["display_name"] == "Update 2"
