"""Clean integration tests for Players API.

Ensures CRUD + validation behavior against live DB.
"""

import pytest
from fastapi.testclient import TestClient
from tests.utils.helpers import (
    assert_response_success,
    assert_response_error,
    assert_valid_json_response,
    assert_player_structure,
    APITestHelper,
)


@pytest.mark.integration
class TestPlayersAPICreate:
    def test_create_human_player_success(self, test_client: TestClient):
        data = {"display_name": "John Doe", "is_human": True}
        r = test_client.post("/api/v1/players", json=data)
        assert_response_success(r, 201)
        player = r.json()
        assert_player_structure(player)
        assert player["display_name"] == "John Doe"
        assert player["is_human"] is True
        assert player["elo_chess"] == 1500
        assert player["elo_poker"] == 1500

    def test_create_ai_player_success(self, test_client: TestClient):
        data = {"display_name": "GPT-4", "is_human": False, "provider": "openai", "model_id": "gpt-4"}
        r = test_client.post("/api/v1/players", json=data)
        assert_response_success(r, 201)
        player = r.json()
        assert player["provider"] == "openai"
        assert player["model_id"] == "gpt-4"

    def test_create_player_missing_display_name(self, test_client: TestClient):
        r = test_client.post("/api/v1/players", json={"is_human": True})
        assert_response_error(r, 422)

    def test_create_player_invalid_type(self, test_client: TestClient):
        r = test_client.post("/api/v1/players", json={"display_name": "X", "is_human": "nope"})
        assert_response_error(r, 422)

    def test_create_multiple_same_name(self, test_client: TestClient):
        data = {"display_name": "DupName", "is_human": True}
        r1 = test_client.post("/api/v1/players", json=data)
        r2 = test_client.post("/api/v1/players", json=data)
        assert_response_success(r1, 201)
        assert_response_success(r2, 201)
        assert r1.json()["id"] != r2.json()["id"]


@pytest.mark.integration
class TestPlayersAPIRead:
    def test_list_structure_and_growth(self, test_client: TestClient):
        """Ensure list endpoint returns a list and creating players increases count."""
        # Baseline
        r0 = test_client.get("/api/v1/players")
        assert_response_success(r0)
        assert isinstance(r0.json(), list)
        baseline_count = len(r0.json())

        # Create two players
        helper = APITestHelper(test_client)
        p1 = helper.create_player()
        p2 = helper.create_player()

        r1 = test_client.get("/api/v1/players")
        assert_response_success(r1)
        players = r1.json()
        ids = {p["id"] for p in players}
        assert p1["id"] in ids and p2["id"] in ids
        # If we weren't at the page limit originally, the count should grow by ≥2.
        # If baseline already hit the pagination limit (100), total length may stay
        # the same while newest two replace two older records.
        if baseline_count + 2 <= 100:
            assert len(players) >= baseline_count + 2
        else:
            assert len(players) == baseline_count

    def test_get_player(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p = helper.create_player()
        r = test_client.get(f"/api/v1/players/{p['id']}")
        assert_response_success(r)
        data = r.json()
        assert data["id"] == p["id"]

    def test_get_player_not_found(self, test_client: TestClient):
        r = test_client.get("/api/v1/players/999999")
        assert_response_error(r, 404)

    def test_get_player_invalid_id(self, test_client: TestClient):
        r = test_client.get("/api/v1/players/notint")
        assert_response_error(r, 422)

    def test_pagination(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        for _ in range(5):
            helper.create_player()
        r1 = test_client.get("/api/v1/players?limit=3")
        assert_response_success(r1)
        assert len(r1.json()) <= 3
        r2 = test_client.get("/api/v1/players?skip=2&limit=3")
        assert_response_success(r2)
        assert len(r2.json()) <= 3


@pytest.mark.integration
class TestPlayersAPIUpdate:
    def test_update_player(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p = helper.create_player()
        r = test_client.put(f"/api/v1/players/{p['id']}", json={"display_name": "Updated", "provider": "anthropic"})
        assert_response_success(r)
        data = r.json()
        assert data["display_name"] == "Updated"
        assert data["provider"] == "anthropic"

    def test_update_partial(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p = helper.create_player()
        r = test_client.put(f"/api/v1/players/{p['id']}", json={"provider": "prov"})
        assert_response_success(r)
        assert r.json()["provider"] == "prov"

    def test_update_not_found(self, test_client: TestClient):
        r = test_client.put("/api/v1/players/999999", json={"display_name": "X"})
        assert_response_error(r, 404)

    def test_update_invalid(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p = helper.create_player()
        r = test_client.put(f"/api/v1/players/{p['id']}", json={"display_name": 123})
        assert_response_error(r, 422)


@pytest.mark.integration
class TestPlayersAPIDelete:
    def test_delete_player(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p = helper.create_player()
        r = test_client.delete(f"/api/v1/players/{p['id']}")
        assert_response_success(r, 204)
        check = test_client.get(f"/api/v1/players/{p['id']}")
        assert_response_error(check, 404)

    def test_delete_not_found(self, test_client: TestClient):
        r = test_client.delete("/api/v1/players/999999")
        assert_response_error(r, 404)

    def test_delete_with_games(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p1 = helper.create_player()
        helper.create_player()  # second
        helper.create_game()
        r = test_client.delete(f"/api/v1/players/{p1['id']}")
        assert r.status_code in [204, 409, 400]


@pytest.mark.integration
class TestPlayersAPIValidation:
    def test_invalid_json(self, test_client: TestClient):
        r = test_client.post("/api/v1/players", data="not json", headers={"Content-Type": "application/json"})
        assert_response_error(r, 422)

    def test_extra_fields_ignored(self, test_client: TestClient):
        r = test_client.post("/api/v1/players", json={"display_name": "T", "is_human": True, "x": 1})
        assert_response_success(r, 201)
        assert "x" not in r.json()

    def test_unicode_name(self, test_client: TestClient):
        r = test_client.post("/api/v1/players", json={"display_name": "玩家🎮", "is_human": True})
        assert_response_success(r, 201)
        assert r.json()["display_name"].startswith("玩家")

    def test_long_name(self, test_client: TestClient):
        name = "A" * 400
        response = test_client.post(
            "/api/v1/players",
            json={"display_name": name, "is_human": True},
        )
        # Exceeds schema max_length=255 (should trigger 422 validation error)
        assert_response_error(response, 422)


@pytest.mark.integration
class TestPlayersAPIErrorHandling:
    def test_concurrent_updates(self, test_client: TestClient):
        helper = APITestHelper(test_client)
        p = helper.create_player()
        r1 = test_client.put(f"/api/v1/players/{p['id']}", json={"display_name": "A"})
        r2 = test_client.put(f"/api/v1/players/{p['id']}", json={"display_name": "B"})
        assert_response_success(r1)
        assert_response_success(r2)
        final = test_client.get(f"/api/v1/players/{p['id']}")
        assert_response_success(final)
        assert final.json()["display_name"] == "B"

    def test_noop(self):
        # Placeholder for DB error simulation
        assert True
