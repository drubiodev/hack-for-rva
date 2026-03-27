"""Pydantic v2 request/response schemas — mirrors procurement/docs/openapi.yaml."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# --- Enums as literals (matching OpenAPI spec) ---

DocumentStatus = str  # uploading|ocr_complete|classified|extracted|analyst_review|pending_approval|approved|rejected|error
DocumentType = str  # rfp|rfq|contract|purchase_order|invoice|amendment|cooperative|other
DocumentSource = str  # upload|socrata|sam_gov|eva


# --- Extracted Fields ---


class ExtractedFieldsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    title: str | None = None
    document_number: str | None = None
    vendor_name: str | None = None
    issuing_department: str | None = None
    total_amount: float | None = None
    currency: str = "USD"
    document_date: date | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    contract_type: str | None = None
    payment_terms: str | None = None
    renewal_clause: str | None = None
    insurance_required: bool | None = None
    bond_required: bool | None = None
    scope_summary: str | None = None
    raw_extraction: dict[str, Any] = {}
    extraction_confidence: float | None = None


# --- Validation Result ---


class ValidationResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    rule_code: str
    severity: str
    field_name: str | None = None
    message: str
    suggestion: str | None = None
    resolved: bool = False
    resolved_by: str | None = None
    resolved_at: datetime | None = None


# --- Activity Entry ---


class ActivityEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    action: str
    actor_name: str | None = None
    actor_role: str
    details: dict[str, Any] = {}
    created_at: datetime


# --- Document Summary (list item) ---


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    original_filename: str | None = None
    source: str
    status: str
    document_type: str | None = None
    vendor_name: str | None = None
    total_amount: float | None = None
    expiration_date: date | None = None
    validation_error_count: int = 0
    validation_warning_count: int = 0
    submitted_by: str | None = None
    approved_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


# --- Document Detail ---


class DocumentDetail(DocumentSummary):
    blob_url: str | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None
    page_count: int | None = None
    ocr_text: str | None = None
    ocr_confidence: float | None = None
    classification_confidence: float | None = None
    error_message: str | None = None
    submitted_at: datetime | None = None
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    processed_at: datetime | None = None
    extracted_fields: ExtractedFieldsSchema | None = None
    validations: list[ValidationResultSchema] = []
    activity: list[ActivityEntrySchema] = []


# --- Document List Response ---


class DocumentListResponse(BaseModel):
    items: list[DocumentSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Field Update Request ---


class FieldUpdateRequest(BaseModel):
    updated_by: str
    fields: dict[str, Any] = {}


# --- Analytics Summary ---


class AnalyticsSummarySchema(BaseModel):
    total_documents: int = 0
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_source: dict[str, int] = {}
    total_contract_value: float = 0.0
    documents_processed_today: int = 0


# --- Risk Summary ---


class ExpiringContractSchema(BaseModel):
    id: UUID
    vendor_name: str | None = None
    title: str | None = None
    total_amount: float | None = None
    expiration_date: date
    days_until_expiry: int


class RiskSummarySchema(BaseModel):
    expiring_contracts: list[ExpiringContractSchema] = []
    total_expiring_30: int = 0
    total_expiring_60: int = 0
    total_expiring_90: int = 0


# --- Error Response ---


class ErrorResponse(BaseModel):
    detail: str
