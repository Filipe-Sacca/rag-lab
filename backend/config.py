"""
RAG Lab Backend Configuration

Pydantic settings for environment variables and application configuration.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", alias="ENV")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:9090,http://localhost:5173,http://localhost:3000,http://5.161.109.157:9090"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Google Gemini
    GOOGLE_API_KEY: str = Field(..., description="Google AI API key (primary)")
    GOOGLE_API_KEYS: str = Field(
        default="",
        description="Additional API keys for rotation (comma-separated, from different projects)"
    )
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash")
    EMBEDDING_MODEL: str = Field(default="text-embedding-004")

    # Live API Configuration (unlimited RPM/RPD)
    USE_LIVE_API: bool = Field(
        default=True,
        description="Use Live API for unlimited RPM/RPD (recommended)"
    )
    LIVE_API_FALLBACK: bool = Field(
        default=False,
        description="Fallback to Standard API if Live API fails (WARNING: Standard API has 429 quota limits!)"
    )

    # Pinecone
    PINECONE_API_KEY: str = Field(..., description="Pinecone API key")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1")
    PINECONE_INDEX_NAME: str = Field(default="rag-lab")
    PINECONE_NAMESPACE: str = Field(default="rag-docs", description="Default Pinecone namespace")

    # Cohere
    COHERE_API_KEY: str = Field(..., description="Cohere API key for reranking")

    # RAG Settings
    CHUNK_SIZE: int = Field(default=1000, description="Default chunk size for text splitting")
    CHUNK_OVERLAP: int = Field(default=200, description="Overlap between chunks")
    TOP_K: int = Field(default=5, description="Number of documents to retrieve")
    TEMPERATURE: float = Field(default=0.7, description="LLM temperature")

    # RAGAS Evaluation
    ENABLE_EVALUATION: bool = Field(default=True)
    RAGAS_METRICS: list[str] = Field(
        default=["faithfulness", "answer_relevancy", "context_precision"]
    )


# Global settings instance
settings = Settings()
