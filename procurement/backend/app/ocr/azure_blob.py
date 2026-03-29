"""Upload files to Azure Blob Storage and generate SAS URLs."""

import logging
import os
from datetime import datetime, timedelta, timezone

from app.config import settings

logger = logging.getLogger(__name__)


async def upload_to_blob(file_path: str, filename: str) -> str:
    """Upload file to Azure Blob Storage. Returns a publicly accessible SAS URL.

    Falls back gracefully to a local-passthrough URL if blob storage is
    unavailable — OCR will then use the local temp file directly.
    """
    if "PLACEHOLDER" in settings.azure_blob_connection_string:
        logger.warning("Azure Blob credentials are PLACEHOLDER — skipping upload, will use local file")
        return f"https://local-passthrough/{settings.azure_blob_container_name}/{filename}"

    try:
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

    except Exception as exc:
        logger.warning(
            "Blob upload failed for %s (%s: %s) — falling back to local-passthrough URL",
            filename, type(exc).__name__, str(exc)[:200],
        )
        return f"https://local-passthrough/{settings.azure_blob_container_name}/{filename}"


def regenerate_sas_url(blob_url: str) -> str:
    """Generate a fresh SAS URL from an existing blob URL (with or without old SAS token).

    Used during reprocessing to ensure Azure DI can access the blob.
    """
    if "PLACEHOLDER" in settings.azure_blob_connection_string:
        return blob_url
    if "placeholder" in blob_url.lower() or "local-passthrough" in blob_url.lower():
        return blob_url

    from azure.storage.blob import BlobSasPermissions, generate_blob_sas
    from urllib.parse import unquote, urlparse

    # Strip any existing SAS query params
    base_url = blob_url.split("?")[0]

    # Parse blob name from URL: https://<account>.blob.core.windows.net/<container>/<blob_name>
    parsed = urlparse(base_url)
    path_parts = parsed.path.lstrip("/").split("/", 1)
    if len(path_parts) < 2:
        logger.warning("Could not parse blob name from URL: %s", blob_url)
        return blob_url

    container_name = path_parts[0]
    # URL-decode the blob name — generate_blob_sas needs the raw name, not %20-encoded
    blob_name = unquote(path_parts[1])
    account_name = parsed.hostname.split(".")[0] if parsed.hostname else ""

    account_key = _extract_account_key(settings.azure_blob_connection_string)

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(days=30),
    )

    sas_url = f"{base_url}?{sas_token}"
    logger.info("Regenerated SAS URL for %s (expires in 30 days)", blob_name)
    return sas_url


def _extract_account_key(connection_string: str) -> str:
    """Extract AccountKey from an Azure Storage connection string."""
    for part in connection_string.split(";"):
        if part.strip().startswith("AccountKey="):
            return part.strip()[len("AccountKey="):]
    raise ValueError("AccountKey not found in connection string")
