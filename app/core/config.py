import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/lbm_arena")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "LBM Arena"
    
    # Database Configuration
    echo_sql: bool = False
    
    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
