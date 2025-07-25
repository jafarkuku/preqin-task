"""
Configuration settings for the Commitment Service.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    app_name: str = "Commitment Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8003
    database_url: str = "sqlite:///./commitments.db"
    investor_service_url: str = "http://localhost:8002"
    asset_class_service_url: str = "http://localhost:8001"
    redis_url: Optional[str] = "redis://localhost:6379"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
