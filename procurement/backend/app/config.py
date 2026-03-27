"""Application configuration — all env vars, single source of truth."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic BaseSettings for all configuration.

    Values are read from environment variables or a .env file.
    """

    # Database (Supabase PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/procurement"

    # Azure Blob Storage
    azure_blob_connection_string: str = "PLACEHOLDER"
    azure_blob_container_name: str = "procurement-docs"

    # Azure Document Intelligence (OCR)
    azure_di_endpoint: str = "https://PLACEHOLDER.cognitiveservices.azure.com/"
    azure_di_key: str = "PLACEHOLDER"

    # Azure OpenAI
    azure_openai_endpoint: str = "https://PLACEHOLDER.openai.azure.com/"
    azure_openai_key: str = "PLACEHOLDER"
    azure_openai_deployment: str = "gpt-4.1-nano"
    azure_openai_api_version: str = "2024-12-01-preview"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # File upload limits
    max_file_size_mb: int = 20
    allowed_extensions: str = ".pdf,.png,.jpg,.jpeg,.tiff"

    # Environment
    environment: str = "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_extension_list(self) -> list[str]:
        """Parse comma-separated extensions into a list."""
        return [e.strip() for e in self.allowed_extensions.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
