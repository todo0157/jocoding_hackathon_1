from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "ContractPilot"
    app_env: str = "development"
    debug: bool = True

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-large"

    # Pinecone (선택사항)
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "contract-pilot"

    # Database (선택사항)
    database_url: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
