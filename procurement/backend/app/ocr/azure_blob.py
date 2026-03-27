"""Upload files to Azure Blob Storage."""

import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)


async def upload_to_blob(file_path: str, filename: str) -> str:
    """Upload file to Azure Blob Storage. Returns blob_url."""
    if "PLACEHOLDER" in settings.azure_blob_connection_string:
        logger.warning("Azure Blob credentials are PLACEHOLDER — returning fake URL")
        return f"https://placeholder.blob.core.windows.net/{settings.azure_blob_container_name}/{filename}"

    from azure.storage.blob.aio import BlobServiceClient

    async with BlobServiceClient.from_connection_string(
        settings.azure_blob_connection_string
    ) as client:
        container = client.get_container_client(settings.azure_blob_container_name)

        # Ensure the container exists
        try:
            await container.create_container()
        except Exception:
            pass  # Already exists

        blob = container.get_blob_client(filename)
        with open(file_path, "rb") as f:
            await blob.upload_blob(f, overwrite=True)

        return blob.url
