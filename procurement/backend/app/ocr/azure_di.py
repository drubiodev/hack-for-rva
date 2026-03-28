"""Azure Document Intelligence OCR (prebuilt-read model)."""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def azure_di_ocr(blob_url: str, file_path: str | None = None) -> tuple[str, float]:
    """OCR scanned PDF/image via Azure Document Intelligence. Returns (text, confidence).

    Uses file_path (local bytes) when blob_url is a placeholder; otherwise uses blob_url.
    """
    if "PLACEHOLDER" in settings.azure_di_key:
        logger.warning("Azure DI credentials are PLACEHOLDER — returning empty text")
        return ("", 0.0)

    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    use_local = file_path and "placeholder" in blob_url.lower()

    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

    async with DocumentIntelligenceClient(
        endpoint=settings.azure_di_endpoint,
        credential=AzureKeyCredential(settings.azure_di_key),
    ) as client:
        if use_local:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            poller = await client.begin_analyze_document(
                "prebuilt-read",
                body=file_bytes,
                content_type="application/octet-stream",
            )
        else:
            poller = await client.begin_analyze_document(
                "prebuilt-read",
                body=AnalyzeDocumentRequest(url_source=blob_url),
            )
        result = await poller.result()

        # Concatenate all page content
        text = result.content or ""

        # Average confidence across all pages
        confidences: list[float] = []
        if result.pages:
            for page in result.pages:
                if page.words:
                    for word in page.words:
                        if word.confidence is not None:
                            confidences.append(word.confidence)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        logger.info(
            "Azure DI OCR: %d chars, %.2f avg confidence",
            len(text),
            avg_confidence,
        )
        return (text, avg_confidence)
