from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:3000"
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"
    supabase_url: str | None = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_service_role_key: str | None = Field(
        default=None, validation_alias="SUPABASE_SERVICE_ROLE_KEY"
    )
    supabase_schema: str = Field(default="public", validation_alias="SUPABASE_SCHEMA")

    model_config = SettingsConfigDict(
        env_prefix="CTJ_",
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()
