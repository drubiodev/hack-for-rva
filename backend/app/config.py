from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_deployment_classifier: str = "gpt-41-nano"
    azure_deployment_responder: str = "gpt-4o-mini"
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    frontend_url: str
    environment: str = "development"

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
