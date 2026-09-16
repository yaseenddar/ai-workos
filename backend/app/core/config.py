from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str 
    environment: str 
    redis_url: str 
    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str 
    access_token_expire_minutes: int 
    refresh_token_expire_days: int 

    # minio settings
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "documents"
    minio_secure: bool = False
    
    # embedding settings
    embedding_model: str
    qdrant_url: str 
    
    # llm settings
    # LLM settings
    gemini_api_key: str
    gemini_model: str 
    
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()