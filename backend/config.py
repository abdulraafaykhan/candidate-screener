"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the backend service."""

    openai_api_key: str
    chroma_persist_path: str
    database_url: str
    max_questions_per_session: int
    embedding_model: str
    llm_model: str
    cors_origins: str

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env.example"


settings = Settings()
