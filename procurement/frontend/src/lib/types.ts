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

export type DepartmentCode =
  | "PUBLIC_WORKS"
  | "TRANSPORTATION"
  | "PUBLIC_SAFETY"
  | "FINANCE"
  | "INFORMATION_TECHNOLOGY"
  | "PLANNING_DEVELOPMENT"
  | "PUBLIC_UTILITIES"
  | "PARKS_RECREATION"
  | "HUMAN_RESOURCES"
  | "RISK_MANAGEMENT"
  | "COMMUNITY_DEVELOPMENT"
  | "CITY_ASSESSOR"
  | "PROCUREMENT"
  | "OTHER";

export type ComplianceFlag =
  | "MBE_WBE"
  | "DAVIS_BACON"
  | "ADA"
  | "DRUG_FREE_WORKPLACE"
  | "OSHA"
  | "VDOT_STANDARDS"
  | "ENVIRONMENTAL"
  | "EEO";

export type ProcurementMethod =
  | "COMPETITIVE_BID"
  | "COOPERATIVE_PURCHASE"
  | "SOLE_SOURCE"
  | "EMERGENCY"
  | "RFP"
  | "OTHER";

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
  | "reprocessed"
  | "reminder_set"
  | "reminder_dismissed"
  | "auto_routed";

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
  primary_department?: DepartmentCode | null;
  department_tags?: DepartmentCode[];
  compliance_flags?: ComplianceFlag[];
  mbe_wbe_required?: boolean | null;
  federal_funding?: boolean | null;
  insurance_general_liability_min?: number | null;
  bond_required?: boolean | null;
  procurement_method?: ProcurementMethod | null;
  cooperative_contract_ref?: string | null;
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

export interface FieldConfidences {
  title?: number;
  vendor_name?: number;
  total_amount?: number;
  effective_date?: number;
  expiration_date?: number;
  contract_type?: number;
  payment_terms?: number;
  insurance_required?: number;
  bond_required?: number;
  [key: string]: number | undefined;
}

export interface SourceHighlight {
  field: string;
  offset: number;
  length: number;
  category: "risk" | "compliance" | "financial" | "identity" | "date";
  quote: string;
}

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
  // Department routing (S15)
  department_tags?: DepartmentCode[];
  primary_department?: DepartmentCode | null;
  department_confidence?: number | null;
  // MBE/WBE & compliance (S16)
  mbe_wbe_required?: boolean | null;
  mbe_wbe_details?: string | null;
  federal_funding?: boolean | null;
  compliance_flags?: ComplianceFlag[];
  // Insurance & bonding intelligence (S17)
  insurance_general_liability_min?: number | null;
  insurance_auto_liability_min?: number | null;
  insurance_professional_liability_min?: number | null;
  workers_comp_required?: boolean | null;
  performance_bond_amount?: number | null;
  payment_bond_amount?: number | null;
  liquidated_damages_rate?: string | null;
  // Procurement method (S18)
  procurement_method?: ProcurementMethod | null;
  cooperative_contract_ref?: string | null;
  prequalification_required?: boolean | null;
  raw_extraction?: Record<string, unknown>;
  extraction_confidence?: number | null;
  source_highlights?: SourceHighlight[];
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
  policy_rule_id?: string | null;
  ai_evidence?: string | null;
  ai_confidence?: number | null;
  department?: string | null;
}

// --- Validation Rule Config ---

export type RuleType = "threshold" | "required_field" | "semantic_policy" | "district_check" | "date_window";
export type RuleScope = "global" | "department";
export type RuleStatus = "draft" | "active" | "deprecated";

export interface ValidationRuleConfig {
  id: string;
  name: string;
  description?: string | null;
  rule_type: RuleType;
  scope: RuleScope;
  department?: string | null;
  severity: ValidationSeverity;
  status: RuleStatus;
  policy_statement?: string | null;
  field_name?: string | null;
  operator?: string | null;
  threshold_value?: string | null;
  message_template?: string | null;
  suggestion?: string | null;
  enabled: boolean;
  applies_to_doc_types?: string[] | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ValidationRuleAuditLog {
  id: string;
  rule_id?: string | null;
  rule_name: string;
  action: string;
  changed_by: string;
  changed_at: string;
  old_values?: Record<string, unknown> | null;
  new_values?: Record<string, unknown> | null;
}

export interface DepartmentComplianceCard {
  department: string;
  total_violations?: number;
  error_count: number;
  warning_count: number;
  info_count: number;
  document_count?: number;
  total_documents?: number;
}

export interface ComplianceSummary {
  departments: DepartmentComplianceCard[];
  department_cards: DepartmentComplianceCard[];
  top_triggered_rules: {
    rule_id?: string | null;
    rule_code?: string;
    rule_name?: string | null;
    trigger_count: number;
    resolved_count?: number;
    severity: string;
  }[];
  recent_violations: {
    id?: string;
    document_id: string;
    document_filename?: string;
    rule_code?: string;
    rule_name?: string;
    severity: string;
    message: string;
    triggered_at?: string;
    department?: string | null;
  }[];
  total_violations?: number;
  total_rules_active?: number;
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

export interface ContractReminder {
  id: string;
  document_id: string;
  reminder_date: string;
  created_by: string;
  note?: string | null;
  status: "pending" | "triggered" | "dismissed";
  created_at: string;
  triggered_at?: string | null;
  vendor_name?: string | null;
  title?: string | null;
  expiration_date?: string | null;
}

export interface RiskSummary {
  expiring_contracts: ExpiringContract[];
  total_expiring_30: number;
  total_expiring_60: number;
  total_expiring_90: number;
  triggered_reminders: ContractReminder[];
  pending_reminders_count: number;
}

export interface ErrorResponse {
  detail: string;
}

// --- Chat ---

export interface ChatSource {
  document_id: string;
  title: string | null;
  relevance: number;
  snippet?: string | null;
}

export interface ChatReference {
  index: number;
  document_id: string;
  title: string | null;
  snippet: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  conversation_id: string;
  intent?: string | null;
  references?: ChatReference[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  intent?: string;
  references?: ChatReference[];
}

// --- Intelligence ---

export interface DepartmentSpend {
  group: string;
  document_count: number;
  total_value: number;
  avg_value: number;
  max_value: number;
}

export interface ComplianceGap {
  id: string;
  title: string;
  vendor_name: string | null;
  total_amount: number | null;
  primary_department: string | null;
  missing_fields: string[];
}

export interface VendorConcentration {
  vendor_name: string;
  contract_count: number;
  total_value: number;
  earliest_expiry: string | null;
}

export interface IntelligenceDocument {
  id: string;
  title: string;
  vendor_name: string | null;
  document_type: string | null;
  total_amount: number | null;
  primary_department: string | null;
  expiration_date: string | null;
  procurement_method: string | null;
  status: string;
}

// --- Auth (localStorage, not real auth) ---

export interface ProcurementUser {
  name: string;
  role: "analyst" | "supervisor";
}

// --- Annotations ---

export interface Annotation {
  id: string;
  x: number;
  y: number;
  page: number;
  text: string;
  author: string;
  initials: string;
  time: string;
}

export interface AnnotationCreate {
  x: number;
  y: number;
  page: number;
  text: string;
  author: string;
  initials: string;
}
