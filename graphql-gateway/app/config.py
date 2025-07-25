"""
Configuration settings for the GraphQL Gateway.

Uses Pydantic to automatically load and validate configuration
from environment variables or .env files.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    app_name: str = "GraphQL Gateway"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 8005

    investor_service_url: str = "http://localhost:8002"
    commitment_service_url: str = "http://localhost:8003"
    asset_class_service_url: str = "http://localhost:8001"

    http_timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

    graphql_debug: bool = False
    graphql_introspection: bool = True
    graphql_playground: bool = True

    cache_ttl_seconds: int = 300
    redis_url: Optional[str] = "redis://localhost:6379"

    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
