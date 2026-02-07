from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:3000"
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"

    model_config = SettingsConfigDict(
        env_prefix="CTJ_",
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
