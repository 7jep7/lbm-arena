"""
Pytest configuration and shared fixtures for LBM Arena tests

This module provides:
- Test database setup and teardown
- Common fixtures used across all tests
- Test client configuration
- Mock configurations
"""

import pytest
import asyncio
from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import tempfile
import os

# Import application components
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from tests.test_config import test_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine using the actual configured database"""
    # Use the same database URL as the application
    database_url = settings.database_url
    
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )
    
    # Don't create/drop tables - use existing database schema
    yield engine
    
    # Clean up connections
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_db_engine
    )
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def db_session(test_db_session) -> Generator[Session, None, None]:
    """Alias for test_db_session for backward compatibility"""
    yield test_db_session


@pytest.fixture(scope="function")
def test_client(test_db_session) -> Generator[TestClient, None, None]:
    """Create a test client with test database"""
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_llm_service():
    """Mock LLM service for testing without API calls"""
    with patch('app.services.llm_service.LLMService') as mock:
        # Configure mock responses
        mock_instance = Mock()
        mock_instance.generate_chess_move.return_value = {
            "move": "e2e4",
            "thinking": "Opening with king's pawn"
        }
        mock_instance.generate_poker_action.return_value = {
            "action": "call",
            "thinking": "Good odds to call"
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture(scope="function")
def mock_redis():
    """Mock Redis for testing without Redis dependency"""
    with patch('app.core.redis.redis_client') as mock:
        mock_client = Mock()
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = True
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="function")
def temp_file():
    """Create a temporary file for testing file operations"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    
    # Clean up
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@pytest.fixture(scope="function")
def sample_chess_fen():
    """Provide a sample chess FEN string for testing"""
    return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.fixture(scope="function")
def sample_poker_state():
    """Provide a sample poker game state for testing"""
    return {
        "community_cards": ["2h", "7c", "Kd"],
        "pot": 100,
        "current_bet": 20,
        "players": [
            {
                "id": 1,
                "chips": 500,
                "hole_cards": ["As", "Kh"],
                "folded": False
            },
            {
                "id": 2,
                "chips": 480,
                "hole_cards": ["Qs", "Jd"],
                "folded": False
            }
        ],
        "current_player": 1,
        "betting_round": "flop"
    }


# Test markers for categorizing tests
pytest.mark.unit = pytest.mark.mark("unit", "Unit tests - isolated component testing")
pytest.mark.integration = pytest.mark.mark("integration", "Integration tests - component interaction")
pytest.mark.performance = pytest.mark.mark("performance", "Performance tests - load and speed testing")
pytest.mark.e2e = pytest.mark.mark("e2e", "End-to-end tests - full workflow testing")
pytest.mark.slow = pytest.mark.mark("slow", "Slow tests - may take longer to execute")


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests - isolated component testing")
    config.addinivalue_line("markers", "integration: Integration tests - component interaction")
    config.addinivalue_line("markers", "performance: Performance tests - load and speed testing")
    config.addinivalue_line("markers", "e2e: End-to-end tests - full workflow testing")
    config.addinivalue_line("markers", "slow: Slow tests - may take longer to execute")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip certain tests based on environment"""
    
    # Skip integration tests if disabled
    if not test_settings.is_integration_test_enabled():
        skip_integration = pytest.mark.skip(reason="Integration tests disabled")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
    
    # Skip performance tests if disabled
    if not test_settings.is_performance_test_enabled():
        skip_performance = pytest.mark.skip(reason="Performance tests disabled")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)
