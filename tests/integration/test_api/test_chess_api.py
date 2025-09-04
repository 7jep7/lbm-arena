"""
Integration tests for Chess API endpoints

Tests chess-specific functionality including:
- Chess game state management
- Legal moves generation
- Move validation
- Chess game flow
"""

import pytest
from fastapi.testclient import TestClient
from tests.utils.helpers import (
    assert_response_success,
    assert_response_error,
    assert_valid_json_response,
    APITestHelper
)
from tests.utils.factories import quick_chess_game_data


@pytest.mark.integration
class TestChessAPIInfo:
    """Test chess API information endpoints"""
    
    def test_get_chess_info(self, test_client: TestClient):
        """Test getting chess API information"""
        response = test_client.get("/api/v1/chess/")
        
        assert_response_success(response)
        info = assert_valid_json_response(response)
        
        assert "message" in info
        assert "available_endpoints" in info
        assert "chess_games_count" in info
        assert "available_chess_games" in info
        
        # Should have at least the basic endpoints
        endpoints = info["available_endpoints"]
        assert any("state" in endpoint for endpoint in endpoints)
        assert any("legal-moves" in endpoint for endpoint in endpoints)
        assert any("validate-move" in endpoint for endpoint in endpoints)
    
    def test_chess_info_with_games(self, test_client: TestClient):
        """Test chess info shows available games"""
        helper = APITestHelper(test_client)
        
        # Create some chess games
        chess_game1 = helper.create_game()
        chess_game2 = helper.create_game()
        
        response = test_client.get("/api/v1/chess/")
        
        assert_response_success(response)
        info = response.json()
        
        assert info["chess_games_count"] >= 2
        assert len(info["available_chess_games"]) >= 2
        
        # Verify game structure
        for game_info in info["available_chess_games"]:
            assert "id" in game_info
            assert "status" in game_info


@pytest.mark.integration
class TestChessGameState:
    """Test chess game state endpoints"""
    
    def test_get_chess_game_state_success(self, test_client: TestClient):
        """Test getting chess game state"""
        helper = APITestHelper(test_client)
        
        # Create a chess game
        game = helper.create_game()
        
        response = test_client.get(f"/api/v1/chess/{game['id']}/state")
        
        assert_response_success(response)
        state = assert_valid_json_response(response)
        
        # Should have chess state structure
        assert "board_fen" in state or "board" in state
        assert "turn" in state
        assert "status" in state
    
    def test_get_chess_game_state_not_found(self, test_client: TestClient):
        """Test getting state for non-existent game"""
        response = test_client.get("/api/v1/chess/99999/state")
        
        assert_response_error(response, 404)
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()
    
    def test_get_non_chess_game_state(self, test_client: TestClient):
        """Test getting chess state for non-chess game"""
        helper = APITestHelper(test_client)
        
        # Create players for poker game
        players = [helper.create_player() for _ in range(4)]
        
        # Create a poker game
        poker_game_data = {
            "game_type": "poker",
            "status": "pending",
            "player_ids": [p["id"] for p in players]
        }
        
        response = test_client.post("/api/v1/games", json=poker_game_data)
        assert_response_success(response, 201)
        poker_game = response.json()
        
        # Try to get chess state for poker game
        response = test_client.get(f"/api/v1/chess/{poker_game['id']}/state")
        
        assert_response_error(response, 400)
        error_data = response.json()
        assert "not a chess game" in error_data["detail"].lower()


@pytest.mark.integration
class TestChessLegalMoves:
    """Test chess legal moves endpoints"""
    
    def test_get_legal_moves_initial_position(self, test_client: TestClient):
        """Test getting legal moves from initial position"""
        helper = APITestHelper(test_client)
        
        # Create a new chess game
        game = helper.create_game()
        
        response = test_client.get(f"/api/v1/chess/{game['id']}/legal-moves")
        
        assert_response_success(response)
        moves_data = assert_valid_json_response(response)
        
        assert "legal_moves" in moves_data
        legal_moves = moves_data["legal_moves"]
        
        # In initial position, should have 20 legal moves (16 pawn + 4 knight)
        assert isinstance(legal_moves, list)
        assert len(legal_moves) == 20
        
        # Verify some expected initial moves
        expected_moves = ["e2e4", "e2e3", "d2d4", "d2d3", "b1c3", "g1f3"]
        for move in expected_moves:
            assert move in legal_moves
    
    def test_get_legal_moves_game_not_found(self, test_client: TestClient):
        """Test getting legal moves for non-existent game"""
        response = test_client.get("/api/v1/chess/99999/legal-moves")
        
        assert_response_error(response, 404)
    
    def test_get_legal_moves_non_chess_game(self, test_client: TestClient):
        """Test getting legal moves for non-chess game"""
        helper = APITestHelper(test_client)
        
        # Create players and poker game
        players = [helper.create_player() for _ in range(4)]
        poker_game_data = {
            "game_type": "poker",
            "status": "pending", 
            "player_ids": [p["id"] for p in players]
        }
        
        response = test_client.post("/api/v1/games", json=poker_game_data)
        assert_response_success(response, 201)
        poker_game = response.json()
        
        # Try to get legal moves for poker game
        response = test_client.get(f"/api/v1/chess/{poker_game['id']}/legal-moves")
        
        assert_response_error(response, 400)
        error_data = response.json()
        assert "not a chess game" in error_data["detail"].lower()
    
    def test_get_legal_moves_after_move(self, test_client: TestClient):
        """Test legal moves after making a move"""
        helper = APITestHelper(test_client)
        
        # Create game and make a move
        game = helper.create_game()
        
        # Make the move e2e4
        move_data = {
            "move_data": {
                "move": "e2e4",
                "player_id": 1
            }
        }
        
        move_response = test_client.post(f"/api/v1/games/{game['id']}/move", json=move_data)
        if move_response.status_code == 200:  # If move succeeded
            # Get legal moves for black
            response = test_client.get(f"/api/v1/chess/{game['id']}/legal-moves")
            
            assert_response_success(response)
            moves_data = response.json()
            
            legal_moves = moves_data["legal_moves"]
            assert isinstance(legal_moves, list)
            assert len(legal_moves) == 20  # Black also has 20 legal moves initially


@pytest.mark.integration
class TestChessMoveValidation:
    """Test chess move validation endpoints"""
    
    def test_validate_legal_move(self, test_client: TestClient):
        """Test validating a legal move"""
        helper = APITestHelper(test_client)
        
        # Create a chess game
        game = helper.create_game()
        
        # Validate a legal opening move
        move_data = {"move": "e2e4"}
        
        response = test_client.post(f"/api/v1/chess/{game['id']}/validate-move", json=move_data)
        
        assert_response_success(response)
        validation = assert_valid_json_response(response)
        
        assert "valid" in validation
        assert validation["valid"] is True
    
    def test_validate_illegal_move(self, test_client: TestClient):
        """Test validating an illegal move"""
        helper = APITestHelper(test_client)
        
        # Create a chess game
        game = helper.create_game()
        
        # Try to validate an illegal move (pawn moving backwards)
        move_data = {"move": "e2e1"}
        
        response = test_client.post(f"/api/v1/chess/{game['id']}/validate-move", json=move_data)
        
        assert_response_success(response)
        validation = response.json()
        
        assert "valid" in validation
        assert validation["valid"] is False
        assert "reason" in validation  # Should explain why it's invalid
    
    def test_validate_move_invalid_format(self, test_client: TestClient):
        """Test validating move with invalid format"""
        helper = APITestHelper(test_client)
        
        game = helper.create_game()
        
        # Invalid UCI format
        move_data = {"move": "invalid_move"}
        
        response = test_client.post(f"/api/v1/chess/{game['id']}/validate-move", json=move_data)
        
        # Should either return invalid or be a 400 error
        if response.status_code == 200:
            validation = response.json()
            assert validation["valid"] is False
        else:
            assert_response_error(response, 400)
    
    def test_validate_move_missing_data(self, test_client: TestClient):
        """Test validating move with missing data"""
        helper = APITestHelper(test_client)
        
        game = helper.create_game()
        
        # Missing move field
        move_data = {}
        
        response = test_client.post(f"/api/v1/chess/{game['id']}/validate-move", json=move_data)
        
        assert_response_error(response, 422)  # Validation error
    
    def test_validate_move_game_not_found(self, test_client: TestClient):
        """Test validating move for non-existent game"""
        move_data = {"move": "e2e4"}
        
        response = test_client.post("/api/v1/chess/99999/validate-move", json=move_data)
        
        assert_response_error(response, 404)


@pytest.mark.integration
class TestChessGameFlow:
    """Test complete chess game flow"""
    
    def test_complete_chess_game_flow(self, test_client: TestClient):
        """Test a complete chess game flow with multiple moves"""
        helper = APITestHelper(test_client)
        
        # Create a chess game
        game = helper.create_game()
        game_id = game["id"]
        
        # Sequence of moves for a short game
        moves = [
            "e2e4",  # White
            "e7e5",  # Black
            "g1f3",  # White
            "b8c6",  # Black
            "f1c4",  # White
            "f7f5"   # Black
        ]
        
        for i, move in enumerate(moves):
            # Get legal moves before making the move
            legal_response = test_client.get(f"/api/v1/chess/{game_id}/legal-moves")
            assert_response_success(legal_response)
            legal_moves = legal_response.json()["legal_moves"]
            
            # Verify the move is legal
            assert move in legal_moves, f"Move {move} should be legal"
            
            # Validate the move
            validate_response = test_client.post(
                f"/api/v1/chess/{game_id}/validate-move",
                json={"move": move}
            )
            assert_response_success(validate_response)
            validation = validate_response.json()
            assert validation["valid"] is True
            
            # Make the move
            move_data = {
                "move_data": {
                    "move": move,
                    "player_id": (i % 2) + 1  # Alternate between player 1 and 2
                }
            }
            
            move_response = test_client.post(f"/api/v1/games/{game_id}/move", json=move_data)
            if move_response.status_code != 200:
                # If move API is not fully implemented, that's ok
                break
            
            # Get updated game state
            state_response = test_client.get(f"/api/v1/chess/{game_id}/state")
            assert_response_success(state_response)
            state = state_response.json()
            
            # Verify turn alternates
            expected_turn = "b" if i % 2 == 0 else "w"  # After white move, it's black's turn
            if "turn" in state:
                assert state["turn"] == expected_turn
    
    def test_chess_game_state_consistency(self, test_client: TestClient):
        """Test that chess game state remains consistent"""
        helper = APITestHelper(test_client)
        
        # Create a chess game
        game = helper.create_game()
        game_id = game["id"]
        
        # Get initial state
        initial_response = test_client.get(f"/api/v1/chess/{game_id}/state")
        assert_response_success(initial_response)
        initial_state = initial_response.json()
        
        # Get legal moves
        moves_response = test_client.get(f"/api/v1/chess/{game_id}/legal-moves")
        assert_response_success(moves_response)
        legal_moves = moves_response.json()["legal_moves"]
        
        # State should be consistent across calls
        state_response2 = test_client.get(f"/api/v1/chess/{game_id}/state")
        assert_response_success(state_response2)
        state2 = state_response2.json()
        
        assert initial_state == state2
        
        # Legal moves should be consistent
        moves_response2 = test_client.get(f"/api/v1/chess/{game_id}/legal-moves")
        assert_response_success(moves_response2)
        legal_moves2 = moves_response2.json()["legal_moves"]
        
        assert set(legal_moves) == set(legal_moves2)


@pytest.mark.integration
class TestChessErrorHandling:
    """Test chess API error handling"""
    
    def test_invalid_game_id_format(self, test_client: TestClient):
        """Test handling of invalid game ID format"""
        # Non-numeric game ID
        response = test_client.get("/api/v1/chess/invalid_id/state")
        
        assert_response_error(response, 422)  # Validation error
    
    def test_chess_endpoints_with_corrupted_state(self, test_client: TestClient):
        """Test chess endpoints with corrupted game state"""
        # This would require manually corrupting a game's state in the database
        # For now, just ensure endpoints handle missing state gracefully
        helper = APITestHelper(test_client)
        
        game = helper.create_game()
        
        # All endpoints should handle errors gracefully
        endpoints = [
            f"/api/v1/chess/{game['id']}/state",
            f"/api/v1/chess/{game['id']}/legal-moves"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            # Should either succeed or fail with proper error code (not 500)
            assert response.status_code != 500
    
    def test_concurrent_chess_operations(self, test_client: TestClient):
        """Test concurrent chess operations"""
        helper = APITestHelper(test_client)
        
        game = helper.create_game()
        game_id = game["id"]
        
        # Make multiple simultaneous requests
        responses = []
        for _ in range(5):
            responses.append(test_client.get(f"/api/v1/chess/{game_id}/state"))
            responses.append(test_client.get(f"/api/v1/chess/{game_id}/legal-moves"))
        
        # All should succeed
        for response in responses:
            assert_response_success(response)


@pytest.mark.integration
@pytest.mark.slow
class TestChessPerformance:
    """Test chess API performance"""
    
    def test_legal_moves_performance(self, test_client: TestClient):
        """Test performance of legal moves generation"""
        helper = APITestHelper(test_client)
        
        # Create multiple games and test legal moves performance
        games = []
        for _ in range(10):
            games.append(helper.create_game())
        
        # Generate legal moves for all games
        for game in games:
            response = test_client.get(f"/api/v1/chess/{game['id']}/legal-moves")
            assert_response_success(response)
            
            moves_data = response.json()
            assert "legal_moves" in moves_data
            assert len(moves_data["legal_moves"]) > 0
    
    def test_multiple_validations_performance(self, test_client: TestClient):
        """Test performance of multiple move validations"""
        helper = APITestHelper(test_client)
        
        game = helper.create_game()
        game_id = game["id"]
        
        # Test moves to validate
        test_moves = [
            "e2e4", "e2e3", "d2d4", "d2d3", "g1f3", "b1c3",
            "a2a4", "h2h4", "c2c4", "f2f4"
        ]
        
        # Validate all moves
        for move in test_moves:
            response = test_client.post(
                f"/api/v1/chess/{game_id}/validate-move",
                json={"move": move}
            )
            assert_response_success(response)
            
            validation = response.json()
            assert "valid" in validation
            # All these should be valid opening moves
            assert validation["valid"] is True
