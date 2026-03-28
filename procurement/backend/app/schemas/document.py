"""Pydantic v2 request/response schemas — mirrors procurement/docs/openapi.yaml."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    # Department routing (S15)
    department_tags: list[str] = []
    primary_department: str | None = None
    department_confidence: float | None = None
    # MBE/WBE & compliance (S16)
    mbe_wbe_required: bool | None = None
    mbe_wbe_details: str | None = None
    federal_funding: bool | None = None
    compliance_flags: list[str] = []
    # Insurance & bonding intelligence (S17)
    insurance_general_liability_min: float | None = None
    insurance_auto_liability_min: float | None = None
    insurance_professional_liability_min: float | None = None
    workers_comp_required: bool | None = None
    performance_bond_amount: float | None = None
    payment_bond_amount: float | None = None
    liquidated_damages_rate: str | None = None
    # Procurement method (S18)
    procurement_method: str | None = None
    cooperative_contract_ref: str | None = None
    prequalification_required: bool | None = None
    raw_extraction: dict[str, Any] = {}
    extraction_confidence: float | None = None
    source_highlights: list[dict[str, Any]] | None = None


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
    policy_rule_id: UUID | None = None
    ai_evidence: str | None = None
    ai_confidence: float | None = None


# --- Validation Rule Config ---


class ValidationRuleConfigCreate(BaseModel):
    name: str
    description: str | None = None
    rule_type: str  # threshold, required_field, semantic_policy, district_check, date_window
    scope: str = "global"
    department: str | None = None
    severity: str = "warning"
    policy_statement: str | None = None
    field_name: str | None = None
    operator: str | None = None
    threshold_value: str | None = None
    message_template: str | None = None
    suggestion: str | None = None
    applies_to_doc_types: list[str] | None = None
    created_by: str


class ValidationRuleConfigUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    severity: str | None = None
    scope: str | None = None
    department: str | None = None
    policy_statement: str | None = None
    field_name: str | None = None
    operator: str | None = None
    threshold_value: str | None = None
    message_template: str | None = None
    suggestion: str | None = None
    applies_to_doc_types: list[str] | None = None
    updated_by: str


class ValidationRuleConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    rule_type: str
    scope: str
    department: str | None = None
    severity: str
    status: str
    policy_statement: str | None = None
    field_name: str | None = None
    operator: str | None = None
    threshold_value: str | None = None
    message_template: str | None = None
    suggestion: str | None = None
    enabled: bool
    applies_to_doc_types: list[str] | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime


class ValidationRuleAuditLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rule_id: UUID | None = None
    rule_name: str
    action: str
    changed_by: str
    changed_at: datetime
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None


# --- Compliance Summary ---


class DepartmentComplianceCard(BaseModel):
    department: str
    total_violations: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    document_count: int = 0


class TriggeredRuleSummary(BaseModel):
    rule_id: UUID | None = None
    rule_code: str
    rule_name: str | None = None
    severity: str
    trigger_count: int


class RecentViolation(BaseModel):
    id: UUID
    document_id: UUID
    document_title: str | None = None
    vendor_name: str | None = None
    rule_code: str
    severity: str
    message: str
    department: str | None = None
    created_at: datetime | None = None


class ComplianceSummary(BaseModel):
    department_cards: list[DepartmentComplianceCard] = []
    top_triggered_rules: list[TriggeredRuleSummary] = []
    recent_violations: list[RecentViolation] = []
    total_violations: int = 0
    total_rules_active: int = 0


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
    # Intelligence columns for list view
    primary_department: str | None = None
    department_tags: list[str] = []
    compliance_flags: list[str] = []
    mbe_wbe_required: bool | None = None
    federal_funding: bool | None = None
    insurance_general_liability_min: float | None = None
    bond_required: bool | None = None
    procurement_method: str | None = None
    cooperative_contract_ref: str | None = None


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


class ReminderCreateRequest(BaseModel):
    reminder_date: date
    created_by: str
    note: str | None = None


class ReminderUpdateRequest(BaseModel):
    status: str
    dismissed_by: str


class ReminderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    reminder_date: date
    created_by: str
    note: str | None = None
    status: str
    created_at: datetime
    triggered_at: datetime | None = None
    vendor_name: str | None = None
    title: str | None = None
    expiration_date: date | None = None


class RiskSummarySchema(BaseModel):
    expiring_contracts: list[ExpiringContractSchema] = []
    total_expiring_30: int = 0
    total_expiring_60: int = 0
    total_expiring_90: int = 0
    triggered_reminders: list[ReminderSchema] = []
    pending_reminders_count: int = 0


# --- Annotations ---


class AnnotationCreate(BaseModel):
    x: float
    y: float
    page: int = Field(default=1, ge=1, le=9999)
    text: str = Field(..., min_length=1, max_length=2000)
    author: str = Field(..., min_length=1, max_length=200)
    initials: str = Field(..., min_length=1, max_length=5)


class AnnotationResponse(BaseModel):
    id: str
    x: float
    y: float
    page: int
    text: str
    author: str
    initials: str
    time: str


# --- Error Response ---


class ErrorResponse(BaseModel):
    detail: str


# --- Approval workflow requests ---


class SubmitRequest(BaseModel):
    submitted_by: str


class ApproveRequest(BaseModel):
    approved_by: str
    comments: str | None = None


class RejectRequest(BaseModel):
    rejected_by: str
    reason: str


class ReprocessRequest(BaseModel):
    requested_by: str


# --- Chat ---


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None


class ChatSourceSchema(BaseModel):
    document_id: UUID
    title: str | None = None
    relevance: float
    snippet: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSourceSchema]
    conversation_id: str
    intent: str | None = None
