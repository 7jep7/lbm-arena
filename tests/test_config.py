"""
Test configuration and settings for LBM Arena

This module provides configuration specific to testing, including:
- Test database settings
- Mock configurations
- Test-specific environment variables
"""

import os
from typing import Optional

class TestSettings:
    """Test-specific configuration settings"""
    
    # Database settings
    TEST_DATABASE_URL: str = os.getenv(
        "TEST_DATABASE_URL", 
        "sqlite:///./test_lbm_arena.db"
    )
    
    # Use in-memory SQLite for fastest tests
    MEMORY_DATABASE_URL: str = "sqlite:///:memory:"
    
    # Redis settings for tests
    TEST_REDIS_URL: str = os.getenv(
        "TEST_REDIS_URL",
        "redis://localhost:6379/1"  # Use DB 1 for tests
    )
    
    # LLM API settings (mocked in tests)
    TEST_OPENAI_API_KEY: str = "test-openai-key"
    TEST_ANTHROPIC_API_KEY: str = "test-anthropic-key"
    
    # Test environment flags
    TESTING: bool = True
    DEBUG: bool = True
    
    # Test data settings
    TEST_DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    
    # Performance test settings
    PERFORMANCE_TEST_ITERATIONS: int = 100
    PERFORMANCE_MAX_RESPONSE_TIME_MS: int = 500
    
    # Test timeouts
    API_TIMEOUT_SECONDS: int = 30
    DATABASE_TIMEOUT_SECONDS: int = 10
    
    @classmethod
    def get_database_url(cls, use_memory: bool = True) -> str:
        """Get appropriate database URL for tests"""
        if use_memory:
            return cls.MEMORY_DATABASE_URL
        return cls.TEST_DATABASE_URL
    
    @classmethod
    def is_integration_test_enabled(cls) -> bool:
        """Check if integration tests should run"""
        return os.getenv("RUN_INTEGRATION_TESTS", "true").lower() == "true"
    
    @classmethod
    def is_performance_test_enabled(cls) -> bool:
        """Check if performance tests should run"""
        return os.getenv("RUN_PERFORMANCE_TESTS", "false").lower() == "true"


# Global test settings instance
test_settings = TestSettings()
