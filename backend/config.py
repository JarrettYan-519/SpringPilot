from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{BASE_DIR}/springpilot.db"
    upload_dir: str = str(BASE_DIR / "uploads")
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
