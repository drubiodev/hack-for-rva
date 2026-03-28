"""Application configuration — all env vars, single source of truth."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Pydantic BaseSettings for all configuration.

    Values are read from environment variables or a .env file.
    """

    # Database (Azure SQL Server)
    database_url: str = "mssql+aioodbc://hackrva:x70ZTKon9616%24%40q@hackrvasqlserver.database.windows.net:1433/hackrva?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

    # Azure Blob Storage
    azure_blob_connection_string: str = "PLACEHOLDER"
    azure_blob_container_name: str = "procurement-docs"

    # Azure Document Intelligence (OCR)
    azure_di_endpoint: str = "https://PLACEHOLDER.cognitiveservices.azure.com/"
    azure_di_key: str = "PLACEHOLDER"

    # Azure OpenAI
    azure_openai_endpoint: str = "https://PLACEHOLDER.openai.azure.com/"
    azure_openai_key: str = "PLACEHOLDER"
    azure_openai_deployment: str = "chatgpt-5.4-mini"
    azure_openai_api_version: str = "2024-12-01-preview"

    # Azure AI Search (RAG chatbot)
    azure_search_endpoint: str = "https://srch-hackrva.search.windows.net"
    azure_search_key: str = "BzeDyjoGcfk2h1KTEiAYJRIVt20lFrtDcCWueVeDoWAzSeDB0dNT"
    azure_search_index: str = "contracts"

    # Azure AI Foundry project endpoint
    azure_foundry_endpoint: str = "https://af-hackrva.services.ai.azure.com/api/projects/proj-hackrva"

    # Azure Document Intelligence page budget (per server lifetime)
    azure_di_page_budget: int = 400

    # Extraction confidence threshold (0.0-1.0)
    # Fields below this threshold are flagged for human review
    confidence_threshold: float = 0.9

    # CORS
    cors_origins: str = "http://localhost:3000"

    # File upload limits
    max_file_size_mb: int = 100
    allowed_extensions: str = ".pdf,.png,.jpg,.jpeg,.tiff"

    # Azure Application Insights
    applicationinsights_connection_string: str = ""

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
