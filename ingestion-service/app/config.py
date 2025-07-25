"""
Configuration settings for the Ingestion Service.

Uses Pydantic to automatically load and validate configuration
from environment variables or .env files.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class uses Pydantic to automatically load and validate
    configuration from environment variables or .env files.
    """

    app_name: str = "Ingestion Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8004
    asset_class_service_url: str = "http://localhost:8001"
    investor_service_url: str = "http://localhost:8002"
    commitment_service_url: str = "http://localhost:8003"
    batch_size: int = 50
    max_csv_size_mb: int = 100
    job_timeout_minutes: int = 30
    http_timeout_seconds: float = 60.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    redis_url: Optional[str] = "redis://localhost:6379"
    redis_job_ttl_hours: int = 24
    upload_dir: str = "/tmp/ingestion_uploads"
    allowed_file_extensions: list = ["csv", "CSV"]
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    max_rows_per_csv: int = 100000
    required_csv_columns: list = [
        "Investor Name",
        "Investory Type",
        "Investor Country",
        "Investor Date Added",
        "Investor Last Updated",
        "Commitment Asset Class",
        "Commitment Amount",
        "Commitment Currency"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
