from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "production-rag-system"
    env: str = "dev"
    log_level: str = "INFO"

    semantic_cache_ttl_seconds: int = 3600
    conversation_window: int = 10

    model_config = SettingsConfigDict(env_prefix="RAG_", env_file=".env", extra="ignore")


settings = Settings()
