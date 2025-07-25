from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class uses Pydantic to automatically load and validate
    configuration from environment variables or .env files.
    """

    # Application settings
    app_name: str = "Investors Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8002

    # MongoDB settings
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "investors_db"
    collection_name: str = "investors"

    # External service URLs (for data enrichment)
    asset_class_service_url: str = "http://localhost:8001"
    commitment_service_url: str = "http://localhost:8003"

    # Redis settings (for future caching)
    redis_url: Optional[str] = None

    log_level: str = "INFO"

    class Config:
        # Load from .env file if present
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
