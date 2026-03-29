"""Azure Document Intelligence OCR (prebuilt-read model)."""

import asyncio
import logging
import os
import tempfile

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level page budget counter (resets on server restart)
_di_pages_used = 0

MAX_CHUNK_BYTES = 3_500_000  # 3.5 MB — safely under Azure DI's 4 MB local-upload limit
MAX_PAGES = 100  # Budget guard: skip pages beyond this for very large documents


async def _chunked_ocr(
    file_path: str, client, max_chunk_bytes: int = MAX_CHUNK_BYTES, max_pages: int = MAX_PAGES
) -> tuple[str, float, dict]:
    """Split large PDFs into page-range chunks, OCR each, concatenate results."""
    global _di_pages_used
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    pages_to_process = min(total_pages, max_pages)

    if pages_to_process < total_pages:
        logger.warning(
            "PDF has %d pages, only processing first %d to stay within budget",
            total_pages,
            max_pages,
        )

    all_text: list[str] = []
    all_confidences: list[float] = []
    all_metadata_pages: list[dict] = []

    chunk_start = 0
    while chunk_start < pages_to_process:
        chunk_end = min(chunk_start + 20, pages_to_process)

        # Try progressively smaller chunks until one fits under the size limit
        tmp_path: str | None = None
        while chunk_end > chunk_start:
            writer = PdfWriter()
            for i in range(chunk_start, chunk_end):
                writer.add_page(reader.pages[i])

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            writer.write(tmp)
            tmp.close()
            tmp_path = tmp.name

            if os.path.getsize(tmp_path) <= max_chunk_bytes:
                break

            os.unlink(tmp_path)
            tmp_path = None
            chunk_end = chunk_start + (chunk_end - chunk_start) // 2
            if chunk_end <= chunk_start:
                chunk_end = chunk_start + 1  # At minimum, try a single page

        if tmp_path is None:
            chunk_start = chunk_end
            continue

        try:
            with open(tmp_path, "rb") as f:
                chunk_bytes = f.read()

            poller = await client.begin_analyze_document(
                "prebuilt-read",
                body=chunk_bytes,
                content_type="application/octet-stream",
            )
            result = await asyncio.wait_for(poller.result(), timeout=120)

            text = result.content or ""
            all_text.append(text)

            chunk_page_count = len(result.pages) if result.pages else 0
            _di_pages_used += chunk_page_count

            if result.pages:
                for page in result.pages:
                    if page.words:
                        for word in page.words:
                            if word.confidence is not None:
                                all_confidences.append(word.confidence)
                    page_info: dict = {
                        "page": page.page_number,
                        "width": page.width,
                        "height": page.height,
                        "unit": page.unit,
                    }
                    if page.spans:
                        page_info["offset"] = page.spans[0].offset
                        page_info["length"] = page.spans[0].length
                    all_metadata_pages.append(page_info)

            logger.info(
                "  Chunk pages %d-%d: %d chars OCR'd (budget %d/%d)",
                chunk_start + 1,
                chunk_end,
                len(text),
                _di_pages_used,
                settings.azure_di_page_budget,
            )
        except Exception as e:
            logger.warning("  Chunk pages %d-%d failed: %s", chunk_start + 1, chunk_end, e)
        finally:
            os.unlink(tmp_path)

        chunk_start = chunk_end

    full_text = "\n".join(all_text)
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

    metadata = {"pages": all_metadata_pages}
    logger.info(
        "Chunked OCR complete: %d total chars, %.2f avg confidence from %d pages",
        len(full_text),
        avg_confidence,
        pages_to_process,
    )
    return (full_text, avg_confidence, metadata)


async def azure_di_ocr(blob_url: str, file_path: str | None = None) -> tuple[str, float, dict]:
    """OCR scanned PDF/image via Azure Document Intelligence. Returns (text, confidence, metadata).

    Uses file_path (local bytes) when blob_url is a placeholder; otherwise uses blob_url.
    """
    global _di_pages_used

    if "PLACEHOLDER" in settings.azure_di_key:
        logger.warning("Azure DI credentials are PLACEHOLDER — returning empty text")
        return ("", 0.0, {})

    if _di_pages_used >= settings.azure_di_page_budget:
        logger.warning(
            "Azure DI page budget exhausted (%d/%d) — skipping OCR",
            _di_pages_used,
            settings.azure_di_page_budget,
        )
        return ("", 0.0, {})

    from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

    async with DocumentIntelligenceClient(
        endpoint=settings.azure_di_endpoint,
        credential=AzureKeyCredential(settings.azure_di_key),
    ) as client:
        # Large local files: always chunk locally (DI has 4MB URL limit)
        if file_path and os.path.exists(file_path) and os.path.getsize(file_path) > MAX_CHUNK_BYTES:
            logger.info(
                "File %s is %.1f MB — using chunked local OCR",
                file_path,
                os.path.getsize(file_path) / 1_000_000,
            )
            return await _chunked_ocr(file_path, client)

        # Prefer local bytes when available — avoids Azure DI URL-download issues with
        # filenames that contain spaces or special characters in the blob SAS URL.
        if file_path and os.path.exists(file_path):
            logger.info("Using local bytes for DI OCR: %s", file_path)
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            poller = await client.begin_analyze_document(
                "prebuilt-read",
                body=file_bytes,
                content_type="application/octet-stream",
            )
        elif blob_url and "local-passthrough" not in blob_url.lower() and "placeholder" not in blob_url.lower():
            # Temp file already deleted (e.g. reprocessing) — fall back to SAS URL
            logger.info("Temp file not available; using blob SAS URL for DI OCR: %s", blob_url[:80])
            poller = await client.begin_analyze_document(
                "prebuilt-read",
                body=AnalyzeDocumentRequest(url_source=blob_url),
            )
        else:
            logger.error("No local file and placeholder blob URL — cannot OCR")
            return ("", 0.0, {})
        result = await asyncio.wait_for(poller.result(), timeout=120)

        # Concatenate all page content
        text = result.content or ""

        # Average confidence across all pages
        confidences: list[float] = []
        metadata: dict = {"pages": []}
        if result.pages:
            for page in result.pages:
                if page.words:
                    for word in page.words:
                        if word.confidence is not None:
                            confidences.append(word.confidence)
                page_info: dict = {
                    "page": page.page_number,
                    "width": page.width,
                    "height": page.height,
                    "unit": page.unit,
                }
                if page.spans:
                    page_info["offset"] = page.spans[0].offset
                    page_info["length"] = page.spans[0].length
                metadata["pages"].append(page_info)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        page_count = len(result.pages) if result.pages else 0
        _di_pages_used += page_count
        logger.info(
            "Azure DI OCR: %d chars, %.2f avg confidence (%d pages; budget %d/%d)",
            len(text),
            avg_confidence,
            page_count,
            _di_pages_used,
            settings.azure_di_page_budget,
        )
        return (text, avg_confidence, metadata)
