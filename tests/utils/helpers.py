"""
Test helper functions and utilities

This module provides utility functions that make testing easier and more consistent.
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from contextlib import contextmanager
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient


def assert_response_success(response, expected_status: int = 200):
    """Assert that an API response is successful"""
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_response_error(response, expected_status: int = 400):
    """Assert that an API response is an error"""
    assert response.status_code == expected_status, (
        f"Expected error status {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )


def assert_valid_json_response(response) -> Dict[str, Any]:
    """Parse response JSON and return parsed data.

    This helper does not re-check the HTTP status because tests typically
    call `assert_response_success(response, expected_status)` first.
    """
    try:
        return response.json()
    except json.JSONDecodeError:
        assert False, f"Response is not valid JSON: {response.text}"


def assert_player_structure(player_data: Dict[str, Any], check_id: bool = True):
    """Assert that player data has the correct structure"""
    required_fields = ["display_name", "is_human", "elo_chess", "elo_poker", "created_at"]
    if check_id:
        required_fields.append("id")
    
    for field in required_fields:
        assert field in player_data, f"Missing required field: {field}"
    
    # Type checks
    assert isinstance(player_data["is_human"], bool)
    assert isinstance(player_data["elo_chess"], int)
    assert isinstance(player_data["elo_poker"], int)
    assert player_data["elo_chess"] >= 0
    assert player_data["elo_poker"] >= 0


def assert_game_structure(game_data: Dict[str, Any], check_id: bool = True):
    """Assert that game data has the correct structure"""
    required_fields = ["game_type", "status", "initial_state", "current_state", "created_at"]
    if check_id:
        required_fields.append("id")
    
    for field in required_fields:
        assert field in game_data, f"Missing required field: {field}"
    
    # Type checks
    assert game_data["game_type"] in ["chess", "poker"]
    assert game_data["status"] in ["pending", "waiting", "in_progress", "completed", "aborted"]
    assert isinstance(game_data["initial_state"], dict)
    assert isinstance(game_data["current_state"], dict)


def assert_move_structure(move_data: Dict[str, Any], check_id: bool = True):
    """Assert that move data has the correct structure"""
    required_fields = ["game_id", "player_id", "move_number", "move_data", "created_at"]
    if check_id:
        required_fields.append("id")
    
    for field in required_fields:
        assert field in move_data, f"Missing required field: {field}"
    
    # Type checks
    assert isinstance(move_data["game_id"], int)
    assert isinstance(move_data["player_id"], int)
    assert isinstance(move_data["move_number"], int)
    assert isinstance(move_data["move_data"], dict)


def create_test_players(db: Session, count: int = 2) -> List[Any]:
    """Create test players in the database and return them"""
    from app.models.player import Player
    from tests.utils.factories import PlayerFactory
    
    players = []
    player_data_list = PlayerFactory.create_multiple_players(count)
    
    for player_data in player_data_list[:count]:
        player = Player(**player_data)
        db.add(player)
        db.flush()  # Get the ID without committing
        players.append(player)
    
    db.commit()
    return players


def create_test_game(db: Session, game_type: str = "chess", player_ids: List[int] = None) -> Any:
    """Create a test game in the database and return it"""
    from app.models.game import Game
    from app.models.move import GamePlayer
    from tests.utils.factories import GameFactory, GamePlayerFactory
    
    if player_ids is None:
        # Create test players first
        players = create_test_players(db, 2)
        player_ids = [p.id for p in players]
    
    # Create game data
    if game_type == "chess":
        game_data = GameFactory.create_chess_game(player_ids)
    else:
        game_data = GameFactory.create_poker_game(player_ids)
    
    # Remove player_ids from game_data as it's not a field in the Game model
    player_ids_to_assign = game_data.pop("player_ids")
    
    # Create the game
    game = Game(**game_data)
    db.add(game)
    db.flush()  # Get the ID without committing
    
    # Create game-player relationships
    for i, player_id in enumerate(player_ids_to_assign):
        position = "white" if i == 0 else "black" if game_type == "chess" else f"player_{i}"
        game_player_data = GamePlayerFactory.create_game_player(
            game_id=game.id,
            player_id=player_id,
            position=position
        )
        game_player = GamePlayer(**game_player_data)
        db.add(game_player)
    
    db.commit()
    return game


@contextmanager
def time_test(max_duration_ms: int = 1000):
    """Context manager to assert test execution time"""
    start_time = time.time()
    yield
    duration_ms = (time.time() - start_time) * 1000
    assert duration_ms <= max_duration_ms, (
        f"Test took {duration_ms:.1f}ms, expected <= {max_duration_ms}ms"
    )


def wait_for_condition(
    condition: Callable[[], bool],
    timeout_seconds: int = 5,
    check_interval: float = 0.1
) -> bool:
    """Wait for a condition to become true"""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if condition():
            return True
        time.sleep(check_interval)
    return False


def cleanup_test_data(db: Session):
    """Clean up all test data from the database"""
    from app.models.move import Move, GamePlayer
    from app.models.game import Game
    from app.models.player import Player
    
    # Delete in order to respect foreign key constraints
    db.query(Move).delete()
    db.query(GamePlayer).delete()
    db.query(Game).delete()
    db.query(Player).delete()
    db.commit()


def compare_dict_subset(actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    """Check if actual contains all key-value pairs from expected"""
    for key, value in expected.items():
        if key not in actual:
            return False
        if actual[key] != value:
            return False
    return True


def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
    """Mask sensitive fields in data for safe logging"""
    if sensitive_fields is None:
        sensitive_fields = ["password", "api_key", "token", "secret"]
    
    masked_data = data.copy()
    for field in sensitive_fields:
        if field in masked_data:
            masked_data[field] = "***masked***"
    
    return masked_data


def generate_test_email(prefix: str = "test") -> str:
    """Generate a unique test email address"""
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}@test.example.com"


def generate_test_display_name(prefix: str = "TestPlayer") -> str:
    """Generate a unique test display name"""
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}"


class APITestHelper:
    """Helper class for API testing"""
    
    def __init__(self, client: TestClient):
        self.client = client
    
    def create_player(self, player_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a player via API and return the response data"""
        if player_data is None:
            from tests.utils.factories import quick_player_data
            player_data = quick_player_data()
        
        response = self.client.post("/api/v1/players", json=player_data)
        assert_response_success(response, 201)
        return response.json()
    
    def create_game(self, game_data: Dict[str, Any] = None, *, players: List[Dict[str, Any]] = None, status: str = "pending", game_type: str = "chess") -> Dict[str, Any]:
        """Create a game via API and return the response data.

        Accepts either a full `game_data` dict or convenience args: `players`, `status`, `game_type`.
        """
        if game_data is None:
            # If player objects passed, extract ids; otherwise create two default players
            if players is None:
                player1 = self.create_player()
                player2 = self.create_player()
                player_ids = [player1["id"], player2["id"]]
                players_payload = [
                    {"player_id": player_ids[0], "role": "white"},
                    {"player_id": player_ids[1], "role": "black"}
                ]
            else:
                # Accept either player dicts or ids
                if all(isinstance(p, dict) for p in players):
                    players_payload = [{"player_id": p["id"], "role": p.get("role", "player_0")} for p in players]
                else:
                    players_payload = [{"player_id": p, "role": "player_0"} for p in players]

            game_data = {
                "game_type": game_type,
                "status": status,
                "players": players_payload
            }

        response = self.client.post("/api/v1/games", json=game_data)
        assert_response_success(response, 201)
        return response.json()
    
    def get_players(self) -> List[Dict[str, Any]]:
        """Get all players via API"""
        response = self.client.get("/api/v1/players")
        assert_response_success(response)
        return response.json()
    
    def get_games(self) -> List[Dict[str, Any]]:
        """Get all games via API"""
        response = self.client.get("/api/v1/games")
        assert_response_success(response)
        return response.json()

    def add_moves_to_game(self, game_id: int, moves: List[Dict[str, Any]], expected_status: int = 201) -> List[Dict[str, Any]]:
        """Helper to add multiple moves to a game via the API."""
        results = []
        for m in moves:
            resp = self.client.post(f"/api/v1/games/{game_id}/moves", json=m)
            assert resp.status_code == expected_status, resp.text
            try:
                results.append(resp.json())
            except Exception:
                results.append({"raw": resp.text})
        return results

    def add_moves_to_game(self, game_id: int, count: int = 1, player_id: int | None = None) -> List[Dict[str, Any]]:
        """Create `count` simple moves for a game. If player_id is not provided, use the first player in the game."""
        results = []
        # Fetch game to infer player if needed
        resp = self.client.get(f"/api/v1/games/{game_id}")
        assert_response_success(resp)
        game = resp.json()
        players = game.get("players", [])
        if not players:
            raise AssertionError("No players found in game")
        default_player_id = players[0]["player_id"]
        # Ensure game is in_progress for moves
        if game.get("status") != "in_progress":
            update_resp = self.client.put(f"/api/v1/games/{game_id}", json={"status": "in_progress"})
            assert update_resp.status_code in (200, 201), update_resp.text
            game = self.client.get(f"/api/v1/games/{game_id}").json()
        for i in range(count):
            pid = player_id or default_player_id
            move_payload = {
                "player_id": pid,
                "move_number": i + 1,
                "move_notation": "e4",
                "position_before": game.get("current_state", {}).get("board_fen") if isinstance(game.get("current_state"), dict) else None,
                "position_after": None
            }
            r = self.client.post(f"/api/v1/games/{game_id}/moves", json=move_payload)
            assert r.status_code == 201, r.text
            results.append(r.json())
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check via API"""
        response = self.client.get("/health")
        assert_response_success(response)
        return response.json()

    def get_game_player(self, game_id: int) -> Dict[str, Any]:
        """Return the first player dict for the given game via the API (tests expect a player-like dict)."""
        resp = self.client.get(f"/api/v1/games/{game_id}")
        assert_response_success(resp)
        game = resp.json()
        players = game.get("players", [])
        if not players:
            raise AssertionError("No players found in game")

        # Fetch a full player object using the players API so tests can access 'id' and other fields
        p = players[0]
        player_id = p.get("player_id")
        resp2 = self.client.get(f"/api/v1/players/{player_id}")
        assert_response_success(resp2)
        return resp2.json()

    def update_game(self, game_id: int, payload: Dict[str, Any], expected_status: int = 200) -> Dict[str, Any]:
        """Update a game via API and return the updated resource."""
        response = self.client.put(f"/api/v1/games/{game_id}", json=payload)
        assert_response_success(response, expected_status)
        return response.json()

    def get_game(self, game_id: int) -> Dict[str, Any]:
        """Fetch a game via API and return JSON."""
        response = self.client.get(f"/api/v1/games/{game_id}")
        assert_response_success(response)
        return response.json()

    def get_player(self, player_id: int) -> Dict[str, Any]:
        """Fetch a player by id via API and return JSON."""
        response = self.client.get(f"/api/v1/players/{player_id}")
        assert_response_success(response)
        return response.json()


class DatabaseTestHelper:
    """Helper class for database testing"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    def create_game_with_players(self, players=None):
        """Create a game with players and return (game, players)"""
        from app.models.player import Player as PlayerModel
        from app.models.game import Game as GameModel, GameStatus
        from app.models.move import GamePlayer as GamePlayerModel
        from tests.utils.factories import PlayerFactory
        
        if players is None:
            # Create two players
            player1_data = PlayerFactory.create_human_player()
            player2_data = PlayerFactory.create_ai_player()
            
            player1 = PlayerModel(**player1_data)
            player2 = PlayerModel(**player2_data)
            
            self.db_session.add_all([player1, player2])
            self.db_session.commit()
            
            players = [player1, player2]
        
        # Create game
        game = GameModel(
            game_type="chess",
            status=GameStatus.IN_PROGRESS,
            player1_id=players[0].id,
            player2_id=players[1].id,
            initial_state='{"board_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}',
            current_state='{"board_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}'
        )
        self.db_session.add(game)
        self.db_session.commit()
        
        # Add players to game
        positions = ["white", "black"]
        for i, player in enumerate(players[:2]):  # Only use first 2 players for chess
            game_player = GamePlayerModel(
                game_id=game.id,
                player_id=player.id,
                position=positions[i]
            )
            self.db_session.add(game_player)
        
        self.db_session.commit()
        return game, players


def assert_elo_calculation(
    old_elo: int,
    new_elo: int,
    expected_change_range: tuple = (-50, 50)
):
    """Assert that ELO rating change is within expected range"""
    change = new_elo - old_elo
    min_change, max_change = expected_change_range
    assert min_change <= change <= max_change, (
        f"ELO change {change} not in expected range {expected_change_range}. "
        f"Old: {old_elo}, New: {new_elo}"
    )


def assert_timestamp_recent(timestamp_str: str, max_age_seconds: int = 60):
    """Assert that a timestamp is recent (within max_age_seconds)"""
    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    now = datetime.now(timestamp.tzinfo)
    age = (now - timestamp).total_seconds()
    assert age <= max_age_seconds, (
        f"Timestamp {timestamp_str} is {age:.1f} seconds old, "
        f"expected <= {max_age_seconds} seconds"
    )
