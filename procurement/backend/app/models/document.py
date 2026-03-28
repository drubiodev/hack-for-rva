"""ORM models: Document, ExtractedFields, ValidationResult, ActivityLog."""

import json
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.database import Base


class JsonText(TypeDecorator):
    """Store JSON as NVARCHAR(MAX) text — portable replacement for PostgreSQL JSONB."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blob_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="upload", nullable=False)

    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Duplicate detection
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Processing
    status: Mapped[str] = mapped_column(String(30), default="uploading", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # OCR
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    ocr_metadata: Mapped[dict | None] = mapped_column(JsonText, default=dict)

    # Classification
    document_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    classification_confidence: Mapped[float | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )

    # Approval flow
    submitted_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Annotations (JSON array of annotation objects)
    annotations: Mapped[list | None] = mapped_column(JsonText, default=list)

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    extracted_fields: Mapped["ExtractedFields | None"] = relationship(
        back_populates="document", uselist=False, lazy="selectin"
    )
    validations: Mapped[list["ValidationResult"]] = relationship(
        back_populates="document", lazy="selectin"
    )
    activity: Mapped[list["ActivityLog"]] = relationship(
        back_populates="document", lazy="selectin", order_by="ActivityLog.created_at.desc()"
    )
    reminders: Mapped[list["ContractReminder"]] = relationship(
        back_populates="document", lazy="selectin"
    )


class ExtractedFields(Base):
    __tablename__ = "extracted_fields"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    # Common fields
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issuing_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # Dates
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Contract-specific
    contract_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    renewal_clause: Mapped[str | None] = mapped_column(Text, nullable=True)
    insurance_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    bond_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    scope_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Department routing (S15)
    department_tags: Mapped[list | None] = mapped_column(JsonText, default=list)
    primary_department: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)

    # MBE/WBE & compliance (S16)
    mbe_wbe_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    mbe_wbe_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    federal_funding: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    compliance_flags: Mapped[list | None] = mapped_column(JsonText, default=list)

    # Insurance & bonding intelligence (S17)
    insurance_general_liability_min: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    insurance_auto_liability_min: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    insurance_professional_liability_min: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    workers_comp_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    performance_bond_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    payment_bond_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    liquidated_damages_rate: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Procurement method (S18)
    procurement_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cooperative_contract_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prequalification_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Raw AI output
    raw_extraction: Mapped[dict | None] = mapped_column(JsonText, default=dict)
    extraction_confidence: Mapped[float | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    source_highlights: Mapped[list | None] = mapped_column(JsonText, default=list)

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="extracted_fields")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)

    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Policy rule linkage (NULL for hardcoded system rules)
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("validation_rule_configs.id", ondelete="SET NULL"), nullable=True
    )
    ai_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Numeric(3, 2), nullable=True)

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="validations")


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(30), nullable=False)
    details: Mapped[dict | None] = mapped_column(JsonText, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="activity")


class ContractReminder(Base):
    __tablename__ = "contract_reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    reminder_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="reminders")


class ValidationRuleConfig(Base):
    __tablename__ = "validation_rule_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False)  # threshold, required_field, semantic_policy, district_check, date_window
    scope: Mapped[str] = mapped_column(String(20), default="global", nullable=False)  # global, department
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)  # draft, active, deprecated

    # Semantic policy rules
    policy_statement: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Deterministic rules
    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(20), nullable=True)  # gt, lt, gte, lte, eq, neq, is_empty, is_not_empty
    threshold_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    applies_to_doc_types: Mapped[list | None] = mapped_column(JsonText, nullable=True)

    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ValidationRuleAuditLog(Base):
    __tablename__ = "validation_rule_audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("validation_rule_configs.id", ondelete="SET NULL"), nullable=True
    )
    rule_name: Mapped[str] = mapped_column(String(150), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # created, updated, toggled, status_changed, deleted
    changed_by: Mapped[str] = mapped_column(String(100), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    old_values: Mapped[dict | None] = mapped_column(JsonText, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JsonText, nullable=True)
