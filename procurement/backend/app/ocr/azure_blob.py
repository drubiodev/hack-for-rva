"""Upload files to Azure Blob Storage and generate SAS URLs."""

import logging
import os
from datetime import datetime, timedelta, timezone

from app.config import settings

logger = logging.getLogger(__name__)


async def upload_to_blob(file_path: str, filename: str) -> str:
    """Upload file to Azure Blob Storage. Returns a publicly accessible SAS URL."""
    if "PLACEHOLDER" in settings.azure_blob_connection_string:
        logger.warning("Azure Blob credentials are PLACEHOLDER — returning fake URL")
        return f"https://placeholder.blob.core.windows.net/{settings.azure_blob_container_name}/{filename}"

    from azure.storage.blob import BlobSasPermissions, generate_blob_sas
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

        # Generate a read-only SAS URL valid for 30 days
        # Extract account name and key from connection string
        account_name = blob.account_name
        account_key = _extract_account_key(settings.azure_blob_connection_string)

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=settings.azure_blob_container_name,
            blob_name=filename,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(days=30),
        )

        sas_url = f"{blob.url}?{sas_token}"
        logger.info("Uploaded %s to blob storage with SAS URL (expires in 30 days)", filename)
        return sas_url


def _extract_account_key(connection_string: str) -> str:
    """Extract AccountKey from an Azure Storage connection string."""
    for part in connection_string.split(";"):
        if part.strip().startswith("AccountKey="):
            return part.strip()[len("AccountKey="):]
    raise ValueError("AccountKey not found in connection string")
