from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """

    app_name: str = "Asset Class Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "asset_classes_db"
    collection_name: str = "asset_classes"
    redis_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
