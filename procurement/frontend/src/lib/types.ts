// TypeScript types matching procurement/docs/openapi.yaml exactly.
// Do not modify without updating the OpenAPI spec.

export type DocumentStatus =
  | "uploading"
  | "ocr_complete"
  | "classified"
  | "extracted"
  | "analyst_review"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "error";

export type DocumentType =
  | "rfp"
  | "rfq"
  | "contract"
  | "purchase_order"
  | "invoice"
  | "amendment"
  | "cooperative"
  | "other";

export type DocumentSource = "upload" | "socrata" | "sam_gov" | "eva";

export type ValidationSeverity = "error" | "warning" | "info";

export type ActivityAction =
  | "uploaded"
  | "ocr_complete"
  | "classified"
  | "extracted"
  | "field_edited"
  | "warning_resolved"
  | "submitted"
  | "approved"
  | "rejected"
  | "reprocessed";

export type ActorRole = "analyst" | "supervisor" | "system";

// --- Document schemas ---

export interface DocumentSummary {
  id: string;
  filename: string;
  original_filename?: string;
  source: DocumentSource;
  status: DocumentStatus;
  document_type?: DocumentType;
  vendor_name?: string | null;
  total_amount?: number | null;
  expiration_date?: string | null;
  validation_error_count: number;
  validation_warning_count: number;
  submitted_by?: string | null;
  approved_by?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface DocumentDetail extends DocumentSummary {
  blob_url?: string | null;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  page_count?: number | null;
  ocr_text?: string | null;
  ocr_confidence?: number | null;
  classification_confidence?: number | null;
  error_message?: string | null;
  submitted_at?: string | null;
  approved_at?: string | null;
  rejection_reason?: string | null;
  processed_at?: string | null;
  extracted_fields?: ExtractedFields | null;
  validations?: ValidationResult[];
  activity?: ActivityEntry[];
}

// --- Extracted fields ---

export interface ExtractedFields {
  id: string;
  document_id: string;
  title?: string | null;
  document_number?: string | null;
  vendor_name?: string | null;
  issuing_department?: string | null;
  total_amount?: number | null;
  currency?: string;
  document_date?: string | null;
  effective_date?: string | null;
  expiration_date?: string | null;
  contract_type?: string | null;
  payment_terms?: string | null;
  renewal_clause?: string | null;
  insurance_required?: boolean | null;
  bond_required?: boolean | null;
  scope_summary?: string | null;
  raw_extraction?: Record<string, unknown>;
  extraction_confidence?: number | null;
}

// --- Validation ---

export interface ValidationResult {
  id: string;
  document_id: string;
  rule_code: string;
  severity: ValidationSeverity;
  field_name?: string | null;
  message: string;
  suggestion?: string | null;
  resolved: boolean;
  resolved_by?: string | null;
  resolved_at?: string | null;
}

// --- Activity ---

export interface ActivityEntry {
  id: string;
  document_id: string;
  action: ActivityAction;
  actor_name?: string | null;
  actor_role: ActorRole;
  details?: Record<string, unknown>;
  created_at: string;
}

// --- Request / Response schemas ---

export interface FieldUpdate {
  updated_by: string;
  fields?: Record<string, unknown>;
}

export interface DocumentListResponse {
  items: DocumentSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages?: number;
}

export interface AnalyticsSummary {
  total_documents: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_source: Record<string, number>;
  total_contract_value: number;
  documents_processed_today: number;
}

export interface ExpiringContract {
  id: string;
  vendor_name: string;
  title: string;
  total_amount?: number | null;
  expiration_date: string;
  days_until_expiry: number;
}

export interface RiskSummary {
  expiring_contracts: ExpiringContract[];
  total_expiring_30: number;
  total_expiring_60: number;
  total_expiring_90: number;
}

export interface ErrorResponse {
  detail: string;
}

// --- Auth (localStorage, not real auth) ---

export interface ProcurementUser {
  name: string;
  role: "analyst" | "supervisor";
}
