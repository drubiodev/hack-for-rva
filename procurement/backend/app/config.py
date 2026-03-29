"""Application configuration — all env vars, single source of truth."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings

# Resolve .env relative to this file so config loads correctly regardless of
# the working directory uvicorn is started from.
_ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")


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
    azure_search_key: str = "PLACEHOLDER"
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
    allowed_extensions: str = ".pdf,.png,.jpg,.jpeg,.tiff,.tif"

    # Azure Application Insights
    applicationinsights_connection_string: str = ""

    # Email notifications
    email_enabled: bool = False
    email_smtp_host: str = "smtp.office365.com"
    email_smtp_port: int = 587
    email_smtp_username: str = ""
    email_smtp_password: str = ""
    email_from_address: str = "procurement-noreply@richmondgov.com"
    email_from_name: str = "Richmond Procurement System"
    email_digest_recipients: str = ""
    email_alert_recipients: str = ""
    email_supervisor_recipients: str = ""
    email_user_map: str = "{}"
    email_digest_hour: int = 7
    email_digest_timezone: str = "America/New_York"
    email_weekly_day: int = 0
    app_base_url: str = "http://localhost:3000"

    # Environment
    environment: str = "development"

    model_config = {"env_file": _ENV_FILE, "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_extension_list(self) -> list[str]:
        """Parse comma-separated extensions into a list."""
        return [e.strip() for e in self.allowed_extensions.split(",") if e.strip()]

    @property
    def email_digest_recipient_list(self) -> list[str]:
        return [e.strip() for e in self.email_digest_recipients.split(",") if e.strip()]

    @property
    def email_alert_recipient_list(self) -> list[str]:
        return [e.strip() for e in self.email_alert_recipients.split(",") if e.strip()]

    @property
    def email_supervisor_recipient_list(self) -> list[str]:
        return [e.strip() for e in self.email_supervisor_recipients.split(",") if e.strip()]

    @property
    def email_user_mapping(self) -> dict[str, str]:
        import json
        try:
            return json.loads(self.email_user_map)
        except (json.JSONDecodeError, TypeError):
            return {}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
