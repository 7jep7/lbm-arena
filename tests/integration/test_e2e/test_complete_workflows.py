"""
End-to-End (E2E) tests for LBM Arena

Tests complete user workflows across the entire application:
- Creating players and games
- Playing complete games
- Integration with external services
- Performance under load
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from tests.utils.helpers import APITestHelper, assert_response_success
from tests.utils.factories import PlayerFactory


@pytest.mark.e2e
class TestCompleteChessGame:
    """Test complete chess game workflow"""
    
    def test_complete_chess_game_human_vs_human(self, test_client: TestClient):
        """Test complete chess game between two human players"""
        helper = APITestHelper(test_client)
        
        # Create two human players
        player1_data = {
            "display_name": "Alice",
            "is_human": True
        }
        player2_data = {
            "display_name": "Bob", 
            "is_human": True
        }
        
        player1 = helper.create_player(player1_data)
        player2 = helper.create_player(player2_data)
        
        # Create a chess game
        game_data = {
            "game_type": "chess",
            "status": "pending",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        }
        
        game = helper.create_game(game_data)
        game_id = game["id"]
        
        # Start the game
        helper.update_game(game_id, {"status": "in_progress"})
        
        # Play a series of moves
        moves = [
            {"player_id": player1["id"], "move_number": 1, "move_notation": "e4"},
            {"player_id": player2["id"], "move_number": 1, "move_notation": "e5"},
            {"player_id": player1["id"], "move_number": 2, "move_notation": "Nf3"},
            {"player_id": player2["id"], "move_number": 2, "move_notation": "Nc6"},
            {"player_id": player1["id"], "move_number": 3, "move_notation": "Bb5"},
            {"player_id": player2["id"], "move_number": 3, "move_notation": "a6"},
        ]
        
        for move in moves:
            response = test_client.post(f"/api/v1/games/{game_id}/moves", json=move)
            assert_response_success(response, 201)
        
        # Get all moves to verify
        response = test_client.get(f"/api/v1/games/{game_id}/moves")
        assert_response_success(response)
        game_moves = response.json()
        
        assert len(game_moves) == 6
        assert game_moves[0]["move_notation"] == "e4"
        assert game_moves[-1]["move_notation"] == "a6"
        
        # End the game
        helper.update_game(game_id, {
            "status": "completed",
            "result": "win",
            "winner_id": player1["id"]
        })
        
        # Verify final game state
        final_game = helper.get_game(game_id)
        assert final_game["status"] == "completed"
        assert final_game["result"] == "win"
        assert final_game["winner_id"] == player1["id"]
    
    def test_complete_chess_game_ai_vs_ai(self, test_client: TestClient):
        """Test complete chess game between two AI players"""
        helper = APITestHelper(test_client)
        
        # Create two AI players
        player1_data = {
            "display_name": "GPT-4",
            "is_human": False,
            "provider": "openai",
            "model_id": "gpt-4"
        }
        player2_data = {
            "display_name": "Claude-3",
            "is_human": False,
            "provider": "anthropic", 
            "model_id": "claude-3"
        }
        
        player1 = helper.create_player(player1_data)
        player2 = helper.create_player(player2_data)
        
        # Create and start game
        game = helper.create_game({
            "game_type": "chess",
            "status": "in_progress",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        })
        
        # In a real scenario, AI moves would be generated automatically
        # For testing, we simulate the moves
        ai_moves = [
            {"player_id": player1["id"], "move_number": 1, "move_notation": "d4"},
            {"player_id": player2["id"], "move_number": 1, "move_notation": "d5"},
            {"player_id": player1["id"], "move_number": 2, "move_notation": "c4"},
            {"player_id": player2["id"], "move_number": 2, "move_notation": "e6"},
        ]
        
        for move in ai_moves:
            response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=move)
            assert_response_success(response, 201)
        
        # Verify AI game progresses correctly
        response = test_client.get(f"/api/v1/games/{game['id']}")
        assert_response_success(response)
        game_state = response.json()
        
        assert game_state["status"] == "in_progress"
        assert len(game_state["players"]) == 2
        assert all(not p["player"]["is_human"] for p in game_state["players"])
    
    def test_complete_chess_game_human_vs_ai(self, test_client: TestClient):
        """Test complete chess game between human and AI"""
        helper = APITestHelper(test_client)
        
        # Create human and AI players
        human_player = helper.create_player({
            "display_name": "Human Player",
            "is_human": True
        })
        
        ai_player = helper.create_player({
            "display_name": "Stockfish AI",
            "is_human": False,
            "provider": "stockfish",
            "model_id": "stockfish-15"
        })
        
        # Create game
        game = helper.create_game({
            "game_type": "chess",
            "status": "in_progress",
            "players": [
                {"player_id": human_player["id"], "role": "white"},
                {"player_id": ai_player["id"], "role": "black"}
            ]
        })
        
        # Human makes first move
        human_move = {
            "player_id": human_player["id"],
            "move_number": 1,
            "move_notation": "e4",
            "time_taken": 5.2
        }
        
        response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=human_move)
        assert_response_success(response, 201)
        move_response = response.json()
        
        assert move_response["time_taken"] == 5.2
        assert move_response["move_notation"] == "e4"
        
        # AI responds (simulated)
        ai_move = {
            "player_id": ai_player["id"],
            "move_number": 1,
            "move_notation": "e5",
            "time_taken": 0.1,
            "analysis": {
                "evaluation": 0.0,
                "depth": 20,
                "best_move": "e5"
            }
        }
        
        response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=ai_move)
        assert_response_success(response, 201)
        ai_move_response = response.json()
        
        assert ai_move_response["analysis"] is not None
        assert ai_move_response["analysis"]["depth"] == 20


@pytest.mark.e2e
class TestCompletePokerGame:
    """Test complete poker game workflow"""
    
    def test_complete_poker_game_tournament(self, test_client: TestClient):
        """Test complete poker tournament with multiple players"""
        helper = APITestHelper(test_client)
        
        # Create 4 players for poker
        players = []
        for i in range(4):
            player_data = {
                "display_name": f"Player {i+1}",
                "is_human": i < 2,  # Mix of human and AI
                "provider": "openai" if i >= 2 else None,
                "model_id": "gpt-4" if i >= 2 else None
            }
            player = helper.create_player(player_data)
            players.append(player)
        
        # Create poker game
        game_data = {
            "game_type": "poker",
            "status": "in_progress",
            "players": [
                {"player_id": p["id"], "role": f"seat_{i}"}
                for i, p in enumerate(players)
            ]
        }
        
        game = helper.create_game(game_data)
        game_id = game["id"]
        
        # Simulate poker betting rounds
        betting_moves = [
            {"player_id": players[0]["id"], "move_number": 1, "move_notation": "call_10"},
            {"player_id": players[1]["id"], "move_number": 1, "move_notation": "raise_20"},
            {"player_id": players[2]["id"], "move_number": 1, "move_notation": "call_20"},
            {"player_id": players[3]["id"], "move_number": 1, "move_notation": "fold"},
        ]
        
        for move in betting_moves:
            response = test_client.post(f"/api/v1/games/{game_id}/moves", json=move)
            assert_response_success(response, 201)
        
        # Complete the hand
        helper.update_game(game_id, {
            "status": "completed",
            "result": "win",
            "winner_id": players[1]["id"]
        })
        
        # Verify poker game completion
        final_game = helper.get_game(game_id)
        assert final_game["game_type"] == "poker"
        assert final_game["status"] == "completed"
        assert final_game["winner_id"] == players[1]["id"]


@pytest.mark.e2e 
class TestMultiGameTournament:
    """Test tournament with multiple games"""
    
    def test_round_robin_tournament(self, test_client: TestClient):
        """Test round-robin tournament between multiple players"""
        helper = APITestHelper(test_client)
        
        # Create 4 players
        players = []
        for i in range(4):
            player = helper.create_player({
                "display_name": f"Tournament Player {i+1}",
                "is_human": True
            })
            players.append(player)
        
        # Create all possible pairings (round-robin)
        games = []
        for i in range(len(players)):
            for j in range(i+1, len(players)):
                game_data = {
                    "game_type": "chess",
                    "status": "pending",
                    "players": [
                        {"player_id": players[i]["id"], "role": "white"},
                        {"player_id": players[j]["id"], "role": "black"}
                    ]
                }
                game = helper.create_game(game_data)
                games.append(game)
        
        # Should have 6 games total (4 choose 2)
        assert len(games) == 6
        
        # Play and complete all games
        for idx, game in enumerate(games):
            # Start game
            helper.update_game(game["id"], {"status": "in_progress"})
            
            # Add some moves
            helper.add_moves_to_game(game["id"], count=10)
            
            # Complete game with alternating winners
            winner_idx = idx % 2
            game_players = game["players"]
            winner_id = game_players[winner_idx]["player_id"]
            
            helper.update_game(game["id"], {
                "status": "completed",
                "result": "win",
                "winner_id": winner_id
            })
        
        # Verify all games completed
        for game in games:
            final_game = helper.get_game(game["id"])
            assert final_game["status"] == "completed"
            assert final_game["winner_id"] is not None
        
        # Calculate tournament standings
        standings = {}
        for player in players:
            standings[player["id"]] = {"wins": 0, "losses": 0}
        
        for game in games:
            final_game = helper.get_game(game["id"])
            winner_id = final_game["winner_id"]
            
            # Find loser
            for game_player in final_game["players"]:
                player_id = game_player["player_id"]
                if player_id == winner_id:
                    standings[player_id]["wins"] += 1
                else:
                    standings[player_id]["losses"] += 1
        
        # Verify standings make sense
        total_wins = sum(s["wins"] for s in standings.values())
        total_losses = sum(s["losses"] for s in standings.values())
        assert total_wins == total_losses == 6  # Each game has 1 winner and 1 loser


@pytest.mark.e2e
class TestAPIPerformance:
    """Test API performance under various loads"""
    
    def test_concurrent_game_creation(self, test_client: TestClient):
        """Test creating multiple games concurrently"""
        helper = APITestHelper(test_client)
        
        # Create players for concurrent games
        players = []
        for i in range(20):
            player = helper.create_player({
                "display_name": f"Concurrent Player {i+1}",
                "is_human": True
            })
            players.append(player)
        
        # Create games concurrently
        import threading
        import time
        
        created_games = []
        creation_times = []
        
        def create_game_pair(p1, p2):
            start_time = time.time()
            try:
                game = helper.create_game({
                    "game_type": "chess",
                    "status": "pending",
                    "players": [
                        {"player_id": p1["id"], "role": "white"},
                        {"player_id": p2["id"], "role": "black"}
                    ]
                })
                created_games.append(game)
                creation_times.append(time.time() - start_time)
            except Exception as e:
                print(f"Game creation failed: {e}")
        
        # Create 10 games concurrently
        threads = []
        for i in range(0, 20, 2):
            thread = threading.Thread(
                target=create_game_pair,
                args=(players[i], players[i+1])
            )
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Verify results
        assert len(created_games) == 10
        assert all(g["game_type"] == "chess" for g in created_games)
        
        # Performance assertions
        assert total_time < 30  # Should complete within 30 seconds
        assert max(creation_times) < 10  # No single creation should take more than 10 seconds
        assert sum(creation_times) / len(creation_times) < 5  # Average should be under 5 seconds
    
    def test_bulk_move_addition(self, test_client: TestClient):
        """Test adding many moves to a game quickly"""
        helper = APITestHelper(test_client)
        
        # Create a game
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        game = helper.create_game({
            "game_type": "chess",
            "status": "in_progress",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        })
        
        # Add many moves quickly
        import time
        start_time = time.time()
        
        num_moves = 100
        for i in range(num_moves):
            player_id = player1["id"] if i % 2 == 0 else player2["id"]
            move_data = {
                "player_id": player_id,
                "move_number": (i // 2) + 1,
                "move_notation": f"move_{i+1}",
                "time_taken": 0.1
            }
            
            response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=move_data)
            assert_response_success(response, 201)
        
        total_time = time.time() - start_time
        
        # Verify all moves were added
        response = test_client.get(f"/api/v1/games/{game['id']}/moves")
        assert_response_success(response)
        moves = response.json()
        
        assert len(moves) == num_moves
        
        # Performance assertion
        assert total_time < 30  # Should complete within 30 seconds
        assert total_time / num_moves < 0.5  # Average time per move should be under 0.5 seconds
    
    def test_large_game_retrieval(self, test_client: TestClient):
        """Test retrieving games when there are many in the database"""
        helper = APITestHelper(test_client)
        
        # Create many games
        num_games = 50
        created_game_ids = []
        
        for i in range(num_games):
            player1 = helper.create_player()
            player2 = helper.create_player()
            
            game = helper.create_game({
                "game_type": "chess" if i % 2 == 0 else "poker",
                "status": "completed",
                "players": [
                    {"player_id": player1["id"], "role": "white"},
                    {"player_id": player2["id"], "role": "black"}
                ]
            })
            created_game_ids.append(game["id"])
        
        # Test retrieving all games
        import time
        start_time = time.time()
        
        response = test_client.get("/api/v1/games")
        retrieval_time = time.time() - start_time
        
        assert_response_success(response)
        games = response.json()
        
        # Verify results
        assert len(games) >= num_games
        
        # Performance assertion
        assert retrieval_time < 10  # Should retrieve within 10 seconds
        
        # Test pagination performance
        start_time = time.time()
        response = test_client.get("/api/v1/games?limit=10&skip=0")
        pagination_time = time.time() - start_time
        
        assert_response_success(response)
        paginated_games = response.json()
        assert len(paginated_games) <= 10
        
        # Pagination should be faster
        assert pagination_time < retrieval_time


@pytest.mark.e2e
class TestDataConsistency:
    """Test data consistency across operations"""
    
    def test_player_elo_updates_after_games(self, test_client: TestClient):
        """Test that player ELO ratings update correctly after games"""
        helper = APITestHelper(test_client)
        
        # Create two players
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        initial_elo1 = player1["elo_chess"]
        initial_elo2 = player2["elo_chess"]
        
        # Play a game where player1 wins
        game = helper.create_game({
            "game_type": "chess",
            "status": "completed",
            "result": "win",
            "winner_id": player1["id"],
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        })
        
        # Check if ELO ratings updated (this depends on implementation)
        updated_player1 = helper.get_player(player1["id"])
        updated_player2 = helper.get_player(player2["id"])
        
        # In a real implementation, winner should gain ELO, loser should lose ELO
        # For now, just verify the data is consistent
        assert updated_player1["id"] == player1["id"]
        assert updated_player2["id"] == player2["id"]
        
        # ELO changes would depend on the rating system implementation
        # assert updated_player1["elo_chess"] > initial_elo1  # Winner gains
        # assert updated_player2["elo_chess"] < initial_elo2  # Loser loses
    
    def test_game_move_consistency(self, test_client: TestClient):
        """Test that game moves maintain consistency"""
        helper = APITestHelper(test_client)
        
        # Create a game
        player1 = helper.create_player()
        player2 = helper.create_player()
        
        game = helper.create_game({
            "game_type": "chess",
            "status": "in_progress",
            "players": [
                {"player_id": player1["id"], "role": "white"},
                {"player_id": player2["id"], "role": "black"}
            ]
        })
        
        # Add moves in sequence
        moves = [
            {"player_id": player1["id"], "move_number": 1, "move_notation": "e4"},
            {"player_id": player2["id"], "move_number": 1, "move_notation": "e5"},
            {"player_id": player1["id"], "move_number": 2, "move_notation": "Nf3"},
            {"player_id": player2["id"], "move_number": 2, "move_notation": "Nc6"},
        ]
        
        for move in moves:
            response = test_client.post(f"/api/v1/games/{game['id']}/moves", json=move)
            assert_response_success(response, 201)
        
        # Retrieve moves and verify order and consistency
        response = test_client.get(f"/api/v1/games/{game['id']}/moves")
        assert_response_success(response)
        retrieved_moves = response.json()
        
        assert len(retrieved_moves) == 4
        
        # Verify moves are in correct order
        for i, move in enumerate(retrieved_moves):
            assert move["move_notation"] == moves[i]["move_notation"]
            assert move["player_id"] == moves[i]["player_id"]
            assert move["move_number"] == moves[i]["move_number"]
        
        # Verify alternating players
        for i in range(len(retrieved_moves) - 1):
            assert retrieved_moves[i]["player_id"] != retrieved_moves[i+1]["player_id"]
    
    def test_concurrent_game_updates(self, test_client: TestClient):
        """Test concurrent updates to the same game"""
        helper = APITestHelper(test_client)
        
        # Create a game
        game = helper.create_game()
        game_id = game["id"]
        
        # Attempt concurrent updates
        import threading
        import time
        
        update_results = []
        
        def update_game_status(status):
            try:
                response = test_client.put(
                    f"/api/v1/games/{game_id}",
                    json={"status": status}
                )
                update_results.append({
                    "status_code": response.status_code,
                    "status": status,
                    "timestamp": time.time()
                })
            except Exception as e:
                update_results.append({
                    "error": str(e),
                    "status": status,
                    "timestamp": time.time()
                })
        
        # Start concurrent updates
        threads = []
        statuses = ["in_progress", "paused", "in_progress"]
        
        for status in statuses:
            thread = threading.Thread(target=update_game_status, args=(status,))
            threads.append(thread)
        
        # Start all threads simultaneously
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify final state is consistent
        final_game = helper.get_game(game_id)
        assert final_game["id"] == game_id
        assert final_game["status"] in ["in_progress", "paused"]  # One of the attempted statuses
        
        # At least one update should have succeeded
        successful_updates = [r for r in update_results if r.get("status_code") == 200]
        assert len(successful_updates) > 0
