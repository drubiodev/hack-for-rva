---
description: Debug the document processing pipeline — upload, Azure Blob Storage, Azure Document Intelligence OCR, ChatGPT 5.4 mini classification/extraction, validation engine, and database writes
---

Debug an issue in the HackathonRVA procurement document processing pipeline. Work through the pipeline systematically based on the observed symptom.

---

## Pipeline overview

```
File Upload (multipart)
    ↓
Azure Blob Storage (store original)
    ↓ blob_url
Azure Document Intelligence (prebuilt-read OCR)
    ↓ ocr_text + confidence
ChatGPT 5.4 mini (classify document type)
    ↓ document_type + confidence
ChatGPT 5.4 mini (extract per-type fields)
    ↓ structured fields
Validation Engine (13 rules + AI pass)
    ↓ validation results
Azure PostgreSQL (save all)
    ↓
Document status: validated
```

---

## Symptom → Diagnosis

### "Upload returns error"
1. Check file type validation: only PDF, PNG, JPG, TIFF accepted
2. Check file size: max 20MB
3. Check Azure Blob connection string in `.env`
4. Check container exists: `azure_blob_container_name`
5. Run: `curl -X POST http://localhost:8000/api/v1/documents/upload -F "file=@test.pdf"`

### "Document stuck in uploading status"
1. Check BackgroundTask is triggered after 202 response
2. Check pipeline.py for unhandled exceptions
3. Check Azure Blob upload succeeded: look for blob_url in DB
4. Check logs: `docker logs` or Azure Container Apps logs

### "OCR returns empty text or low confidence"
1. Verify Azure DI endpoint and key in `.env`
2. Check blob_url is accessible (not expired SAS token)
3. Try `prebuilt-read` directly via Azure portal to compare
4. Check page_count — if 0, the document may be image-only without text layer
5. Low confidence (<85%): document may be badly scanned — check validation warning

### "Classification is wrong"
1. Read the OCR text — if OCR is bad, classification will be bad
2. Check `extraction/prompts.py` — is the classifier prompt clear about all 10 types?
3. Check confidence score — low confidence means the model is unsure
4. Try the prompt in Azure OpenAI playground with the same text

### "Extracted fields are null or wrong"
1. Check which extraction prompt was used (matches document_type?)
2. Read the OCR text — is the information actually there?
3. Check `response_format` JSON schema — does it match the Pydantic model?
4. Check `extraction/prompts.py` — does the prompt say "use null if not found"?
5. Compare raw_extraction JSONB in DB with the expected fields

### "Validation results missing or wrong"
1. Check `validation/engine.py` — are all 13 rules implemented?
2. Check rule logic against the extracted fields (dates, amounts, etc.)
3. Check AI validation pass — is it running after rule checks?
4. Verify validation results are saved to `validation_results` table

### "Frontend shows stale data / doesn't update"
1. Check TanStack Query polling interval (5s for detail, 30s for list)
2. Check document status in DB — pipeline may still be running
3. Check CORS — frontend may be getting blocked
4. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`

---

## Quick diagnostic commands

```bash
# Check backend logs
cd procurement/backend && .venv/bin/python -m uvicorn app.main:app --reload 2>&1 | tail -50

# Test upload
curl -X POST http://localhost:8000/api/v1/documents/upload -F "file=@test.pdf" -v

# Check document status in DB
curl http://localhost:8000/api/v1/documents | python -m json.tool

# Check Azure DI connectivity
python -c "from azure.ai.documentintelligence import DocumentIntelligenceClient; print('OK')"

# Check Azure Blob connectivity
python -c "from azure.storage.blob import BlobServiceClient; print('OK')"
```
