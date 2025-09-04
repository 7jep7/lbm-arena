"""
Integration tests for Games API endpoints

Tests the full stack integration of game endpoints including:
- Database operations
- Schema validation
- HTTP status codes
- Response format validation
- Error handling
- CRUD operations
- Game state management
"""

import pytest
from fastapi.testclient import TestClient
from tests.utils.helpers import (
    assert_response_success,
    assert_response_error,
    assert_valid_json_response,
    assert_game_structure,
    APITestHelper
)
from tests.utils.factories import GameFactory


@pytest.mark.integration
class TestGamesAPICreate:
    """Test game creation via API"""
    
    def test_create_chess_game_success(self, test_client: TestClient):
        """Test successful creation of a chess game"""
        helper = APITestHelper(test_client)
        
        # Create players first
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_success(response, 201)
        game = assert_valid_json_response(response)
        assert_game_structure(game)
        
        assert game["game_type"] == "chess"
        assert game["status"] == "pending"
        assert len(game["players"]) == 2
        assert game["result"] is None
        assert game["winner_id"] is None
    
    def test_create_poker_game_success(self, test_client: TestClient):
        """Test successful creation of a poker game"""
        helper = APITestHelper(test_client)
        
        # Create multiple players for poker
        players = [helper.create_player() for _ in range(4)]
        
        game_data = {
            "game_type": "poker",
            "status": "pending",
            "players": [
                {"player_id": p["id"], "role": f"player_{i}"}
                for i, p in enumerate(players)
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_success(response, 201)
        game = assert_valid_json_response(response)
        assert_game_structure(game)
        
        assert game["game_type"] == "poker"
        assert game["status"] == "pending"
        assert len(game["players"]) == 4
    
    def test_create_game_missing_players(self, test_client: TestClient):
        """Test game creation without players fails"""
        game_data = {
            "game_type": "chess",
            "status": "pending"
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 422)  # Validation error
    
    def test_create_game_invalid_game_type(self, test_client: TestClient):
        """Test game creation with invalid game type"""
        helper = APITestHelper(test_client)
        
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        game_data = {
            "game_type": "invalid_game",
            "status": "pending",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 422)
    
    def test_create_game_nonexistent_player(self, test_client: TestClient):
        """Test game creation with non-existent player"""
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": 99999, "role": "white"},
                {"player_id": 99998, "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 404)
    
    def test_create_game_duplicate_player(self, test_client: TestClient):
        """Test game creation with duplicate player"""
        helper = APITestHelper(test_client)
        
        player = helper.create_player()
        
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": player["id"], "role": "white"},
                {"player_id": player["id"], "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 400)  # Business logic error


@pytest.mark.integration
class TestGamesAPIRead:
    """Test game retrieval via API"""
    
    def test_get_all_games_empty(self, test_client: TestClient):
        """Test getting all games when none exist"""
        response = test_client.get("/api/v1/games")
        
        assert_response_success(response)
        games = assert_valid_json_response(response)
        
        assert isinstance(games, list)
        assert len(games) == 0
    
    def test_get_all_games_with_data(self, test_client: TestClient):
        """Test getting all games when some exist"""
        helper = APITestHelper(test_client)
        
        # Create some games
        game1 = helper.create_game()
        game2 = helper.create_game()
        
        response = test_client.get("/api/v1/games")
        
        assert_response_success(response)
        games = assert_valid_json_response(response)
        
        assert isinstance(games, list)
        assert len(games) == 2
        
        # Verify structure of returned games
        for game in games:
            assert_game_structure(game)
        
        # Verify our created games are in the list
        game_ids = [g["id"] for g in games]
        assert game1["id"] in game_ids
        assert game2["id"] in game_ids
    
    def test_get_game_by_id_success(self, test_client: TestClient):
        """Test getting a specific game by ID"""
        helper = APITestHelper(test_client)
        
        # Create a game
        created_game = helper.create_game()
        game_id = created_game["id"]
        
        response = test_client.get(f"/api/v1/games/{game_id}")
        
        assert_response_success(response)
        game = assert_valid_json_response(response)
        assert_game_structure(game)
        
        assert game["id"] == game_id
        assert game["game_type"] == created_game["game_type"]
    
    def test_get_game_by_id_not_found(self, test_client: TestClient):
        """Test getting a non-existent game by ID"""
        response = test_client.get("/api/v1/games/99999")
        
        assert_response_error(response, 404)
    
    def test_get_games_by_player(self, test_client: TestClient):
        """Test getting games filtered by player"""
        helper = APITestHelper(test_client)
        
        # Create players
        player1 = helper.create_player()
        player2 = helper.create_player()
        player3 = helper.create_player()
        
        # Create games with different players
        game1 = helper.create_game(players=[player1, player2])
        game2 = helper.create_game(players=[player1, player3])
        game3 = helper.create_game(players=[player2, player3])
        
        # Get games for player1
        response = test_client.get(f"/api/v1/games?player_id={player1['id']}")
        
        assert_response_success(response)
        games = response.json()
        
        # Should return games 1 and 2
        assert len(games) == 2
        game_ids = [g["id"] for g in games]
        assert game1["id"] in game_ids
        assert game2["id"] in game_ids
        assert game3["id"] not in game_ids
    
    def test_get_games_by_status(self, test_client: TestClient):
        """Test getting games filtered by status"""
        helper = APITestHelper(test_client)
        
        # Create games with different statuses
        game1 = helper.create_game(status="pending")
        game2 = helper.create_game(status="in_progress")
        game3 = helper.create_game(status="completed")
        
        # Get pending games
        response = test_client.get("/api/v1/games?status=pending")
        
        assert_response_success(response)
        games = response.json()
        
        assert len(games) == 1
        assert games[0]["id"] == game1["id"]
        assert games[0]["status"] == "pending"
    
    def test_get_games_pagination(self, test_client: TestClient):
        """Test pagination of games list"""
        helper = APITestHelper(test_client)
        
        # Create several games
        for i in range(5):
            helper.create_game()
        
        # Test with limit
        response = test_client.get("/api/v1/games?limit=3")
        assert_response_success(response)
        games = response.json()
        assert len(games) <= 3
        
        # Test with skip
        response = test_client.get("/api/v1/games?skip=2&limit=3")
        assert_response_success(response)
        games = response.json()
        assert len(games) <= 3


@pytest.mark.integration
class TestGamesAPIUpdate:
    """Test game updates via API"""
    
    def test_update_game_status(self, test_client: TestClient):
        """Test updating game status"""
        helper = APITestHelper(test_client)
        
        # Create a game
        game = helper.create_game(status="pending")
        game_id = game["id"]
        
        # Update status to in_progress
        update_data = {
            "status": "in_progress"
        }
        
        response = test_client.put(f"/api/v1/games/{game_id}", json=update_data)
        
        assert_response_success(response)
        updated_game = assert_valid_json_response(response)
        assert_game_structure(updated_game)
        
        assert updated_game["id"] == game_id
        assert updated_game["status"] == "in_progress"
    
    def test_complete_game_with_winner(self, test_client: TestClient):
        """Test completing a game with a winner"""
        helper = APITestHelper(test_client)
        
        # Create a game
        player1 = helper.create_player()
        player2 = helper.create_player()
        game = helper.create_game(players=[player1, player2], status="in_progress")
        game_id = game["id"]
        
        # Complete the game with player1 as winner
        update_data = {
            "status": "completed",
            "result": "win",
            "winner_id": player1["id"]
        }
        
        response = test_client.put(f"/api/v1/games/{game_id}", json=update_data)
        
        assert_response_success(response)
        updated_game = response.json()
        
        assert updated_game["status"] == "completed"
        assert updated_game["result"] == "win"
        assert updated_game["winner_id"] == player1["id"]
    
    def test_complete_game_draw(self, test_client: TestClient):
        """Test completing a game as a draw"""
        helper = APITestHelper(test_client)
        
        game = helper.create_game(status="in_progress")
        game_id = game["id"]
        
        update_data = {
            "status": "completed",
            "result": "draw",
            "winner_id": None
        }
        
        response = test_client.put(f"/api/v1/games/{game_id}", json=update_data)
        
        assert_response_success(response)
        updated_game = response.json()
        
        assert updated_game["status"] == "completed"
        assert updated_game["result"] == "draw"
        assert updated_game["winner_id"] is None
    
    def test_update_game_not_found(self, test_client: TestClient):
        """Test updating a non-existent game"""
        update_data = {
            "status": "completed"
        }
        
        response = test_client.put("/api/v1/games/99999", json=update_data)
        
        assert_response_error(response, 404)
    
    def test_update_game_invalid_status_transition(self, test_client: TestClient):
        """Test invalid status transitions"""
        helper = APITestHelper(test_client)
        
        # Create a completed game
        game = helper.create_game(status="completed")
        game_id = game["id"]
        
        # Try to change status back to pending
        update_data = {
            "status": "pending"
        }
        
        response = test_client.put(f"/api/v1/games/{game_id}", json=update_data)
        
        # This might succeed or fail depending on business rules
        if response.status_code not in [200, 400]:
            assert False, f"Unexpected status code: {response.status_code}"
    
    def test_update_game_invalid_winner(self, test_client: TestClient):
        """Test setting winner to player not in game"""
        helper = APITestHelper(test_client)
        
        # Create game with two players
        player1 = helper.create_player()
        player2 = helper.create_player()
        player3 = helper.create_player()  # Not in game
        
        game = helper.create_game(players=[player1, player2])
        game_id = game["id"]
        
        # Try to set player3 as winner
        update_data = {
            "status": "completed",
            "result": "win",
            "winner_id": player3["id"]
        }
        
        response = test_client.put(f"/api/v1/games/{game_id}", json=update_data)
        
        assert_response_error(response, 400)


@pytest.mark.integration
class TestGamesAPIDelete:
    """Test game deletion via API"""
    
    def test_delete_game_success(self, test_client: TestClient):
        """Test successful game deletion"""
        helper = APITestHelper(test_client)
        
        # Create a game
        game = helper.create_game()
        game_id = game["id"]
        
        # Delete the game
        response = test_client.delete(f"/api/v1/games/{game_id}")
        
        assert_response_success(response, 204)  # No content
        
        # Verify game is deleted
        response = test_client.get(f"/api/v1/games/{game_id}")
        assert_response_error(response, 404)
    
    def test_delete_game_not_found(self, test_client: TestClient):
        """Test deleting a non-existent game"""
        response = test_client.delete("/api/v1/games/99999")
        
        assert_response_error(response, 404)
    
    def test_delete_game_with_moves(self, test_client: TestClient):
        """Test deleting a game that has moves"""
        helper = APITestHelper(test_client)
        
        # Create a game and add some moves
        game = helper.create_game()
        helper.add_moves_to_game(game["id"], count=5)
        
        # Try to delete the game
        response = test_client.delete(f"/api/v1/games/{game['id']}")
        
        # Should either succeed (cascade delete) or fail with conflict
        if response.status_code not in [204, 409]:
            assert False, f"Unexpected status code: {response.status_code}"


@pytest.mark.integration
class TestGamesAPIMoves:
    """Test game moves via API"""
    
    def test_add_move_to_game(self, test_client: TestClient):
        """Test adding a move to a game"""
        helper = APITestHelper(test_client)
        
        # Create a chess game
        player1 = helper.create_player()
        player2 = helper.create_player()
        game = helper.create_game(
            game_type="chess",
            players=[player1, player2],
            status="in_progress"
        )
        game_id = game["id"]
        
        # Add a move
        move_data = {
            "player_id": player1["id"],
            "move_number": 1,
            "move_notation": "e4",
            "position_before": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "position_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        }
        
        response = test_client.post(f"/api/v1/games/{game_id}/moves", json=move_data)
        
        assert_response_success(response, 201)
        move = response.json()
        
        assert move["player_id"] == player1["id"]
        assert move["move_notation"] == "e4"
        assert move["move_number"] == 1
    
    def test_get_game_moves(self, test_client: TestClient):
        """Test getting all moves for a game"""
        helper = APITestHelper(test_client)
        
        # Create a game and add moves
        game = helper.create_game()
        helper.add_moves_to_game(game["id"], count=10)
        
        response = test_client.get(f"/api/v1/games/{game['id']}/moves")
        
        assert_response_success(response)
        moves = response.json()
        
        assert isinstance(moves, list)
        assert len(moves) == 10
        
        # Moves should be ordered by move_number
        for i, move in enumerate(moves[:-1]):
            assert move["move_number"] <= moves[i + 1]["move_number"]
    
    def test_add_move_invalid_player(self, test_client: TestClient):
        """Test adding move by player not in game"""
        helper = APITestHelper(test_client)
        
        # Create game with two players
        player1 = helper.create_player()
        player2 = helper.create_player()
        player3 = helper.create_player()  # Not in game
        
        game = helper.create_game(players=[player1, player2])
        
        move_data = {
            "player_id": player3["id"],
            "move_number": 1,
            "move_notation": "e4"
        }
        
        response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=move_data)
        
        assert_response_error(response, 400)
    
    def test_add_move_to_completed_game(self, test_client: TestClient):
        """Test adding move to a completed game"""
        helper = APITestHelper(test_client)
        
        game = helper.create_game(status="completed")
        player = helper.get_game_player(game["id"])
        
        move_data = {
            "player_id": player["id"],
            "move_number": 1,
            "move_notation": "e4"
        }
        
        response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=move_data)
        
        assert_response_error(response, 400)


@pytest.mark.integration
class TestGamesAPIValidation:
    """Test API validation and error handling"""
    
    def test_invalid_game_type_enum(self, test_client: TestClient):
        """Test validation of game type enum"""
        helper = APITestHelper(test_client)
        
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        game_data = {
            "game_type": "invalid_type",
            "status": "pending",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 422)
        error_data = response.json()
        assert "game_type" in str(error_data).lower()
    
    def test_invalid_status_enum(self, test_client: TestClient):
        """Test validation of status enum"""
        helper = APITestHelper(test_client)
        
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        game_data = {
            "game_type": "chess",
            "status": "invalid_status",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 422)
    
    def test_missing_required_fields(self, test_client: TestClient):
        """Test validation of required fields"""
        game_data = {
            "status": "pending"
            # Missing game_type and players
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 422)
    
    def test_invalid_player_data_types(self, test_client: TestClient):
        """Test validation of player data types"""
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": "not_an_integer", "role": "white"},
                {"player_id": 2, "role": "black"}
            ]
        }
        
        response = test_client.post("/api/v1/games", json=game_data)
        
        assert_response_error(response, 422)
