from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "EnterpriseOps AI"
    app_env: str = "development"
    debug: bool = True
    database_url: str

    gemini_api_key: str

    #model configuration
    gemini_routine_model: str = "gemma-4-26b-a4b-it"
    gemini_complex_model: str = "gemini-3.5-flash-lite"
    gemini_fallback_model: str = "gemini-3.1-flash-lite"

    model_config= SettingsConfigDict(
        env_file=PROJECT_ROOT/".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()