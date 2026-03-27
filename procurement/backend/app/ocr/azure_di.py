"""Azure Document Intelligence OCR (prebuilt-read model)."""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def azure_di_ocr(blob_url: str) -> tuple[str, float]:
    """OCR scanned PDF/image via Azure Document Intelligence. Returns (text, confidence)."""
    if "PLACEHOLDER" in settings.azure_di_key:
        logger.warning("Azure DI credentials are PLACEHOLDER — returning empty text")
        return ("", 0.0)

    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    async with DocumentIntelligenceClient(
        endpoint=settings.azure_di_endpoint,
        credential=AzureKeyCredential(settings.azure_di_key),
    ) as client:
        poller = await client.begin_analyze_document(
            "prebuilt-read",
            analyze_request={"url_source": blob_url},
            content_type="application/json",
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
