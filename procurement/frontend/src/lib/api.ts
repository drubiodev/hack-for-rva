// Centralized API client — all fetch calls go through this file.
// Never use inline fetch() in components.

import type {
  DocumentListResponse,
  DocumentDetail,
  DocumentSummary,
  ExtractedFields,
  AnalyticsSummary,
  RiskSummary,
  ActivityEntry,
  FieldUpdate,
  DocumentStatus,
  DocumentType,
  DocumentSource,
  ContractReminder,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// --- Helpers ---

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.text();
    let detail = `API error ${res.status}`;
    try {
      const parsed = JSON.parse(body);
      if (parsed.detail) detail = parsed.detail;
    } catch {
      // use default detail
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

// --- Document endpoints ---

export interface FetchDocumentsParams {
  status?: DocumentStatus;
  document_type?: DocumentType;
  source?: DocumentSource;
  page?: number;
  page_size?: number;
  search?: string;
}

export async function fetchDocuments(
  params?: FetchDocumentsParams,
): Promise<DocumentListResponse> {
  const url = new URL(`${BASE}/api/v1/documents`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }
  const res = await fetch(url.toString());
  return handleResponse<DocumentListResponse>(res);
}

export async function fetchDocument(id: string): Promise<DocumentDetail> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}`);
  return handleResponse<DocumentDetail>(res);
}

export async function uploadDocument(
  file: File,
  uploadedBy: string,
): Promise<DocumentSummary> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("uploaded_by", uploadedBy);
  const res = await fetch(`${BASE}/api/v1/documents/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<DocumentSummary>(res);
}

// --- Field editing ---

export async function updateFields(
  id: string,
  data: FieldUpdate,
): Promise<ExtractedFields> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}/fields`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<ExtractedFields>(res);
}

// --- Approval workflow ---

export async function submitForApproval(
  id: string,
  submittedBy: string,
): Promise<DocumentSummary> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ submitted_by: submittedBy }),
  });
  return handleResponse<DocumentSummary>(res);
}

export async function approveDocument(
  id: string,
  approvedBy: string,
  comments?: string,
): Promise<DocumentSummary> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved_by: approvedBy, comments }),
  });
  return handleResponse<DocumentSummary>(res);
}

export async function rejectDocument(
  id: string,
  rejectedBy: string,
  reason: string,
): Promise<DocumentSummary> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rejected_by: rejectedBy, reason }),
  });
  return handleResponse<DocumentSummary>(res);
}

export async function reprocessDocument(
  id: string,
  requestedBy: string,
): Promise<DocumentSummary> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}/reprocess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ requested_by: requestedBy }),
  });
  return handleResponse<DocumentSummary>(res);
}

// --- Review ---

export async function reviewDocument(
  id: string,
  reviewedBy: string,
  role: "analyst" | "supervisor",
  notes?: string,
): Promise<DocumentSummary> {
  const res = await fetch(`${BASE}/api/v1/documents/${id}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reviewed_by: reviewedBy, role, notes }),
  });
  return handleResponse<DocumentSummary>(res);
}

// --- Resolve warning ---

export async function resolveWarning(
  documentId: string,
  validationId: string,
  resolvedBy: string,
): Promise<import("./types").ValidationResult> {
  const res = await fetch(
    `${BASE}/api/v1/documents/${documentId}/resolve-warning`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ validation_id: validationId, resolved_by: resolvedBy }),
    },
  );
  return handleResponse<import("./types").ValidationResult>(res);
}

// --- Analytics ---

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const res = await fetch(`${BASE}/api/v1/analytics/summary`);
  return handleResponse<AnalyticsSummary>(res);
}

export async function fetchRisks(days?: number): Promise<RiskSummary> {
  const url = new URL(`${BASE}/api/v1/analytics/risks`);
  if (days !== undefined) url.searchParams.set("days", String(days));
  const res = await fetch(url.toString());
  return handleResponse<RiskSummary>(res);
}

// --- Activity ---

export async function fetchActivity(
  limit?: number,
): Promise<{ items: ActivityEntry[] }> {
  const url = new URL(`${BASE}/api/v1/activity`);
  if (limit !== undefined) url.searchParams.set("limit", String(limit));
  const res = await fetch(url.toString());
  return handleResponse<{ items: ActivityEntry[] }>(res);
}

// --- Chat ---

export async function sendChatMessage(
  question: string,
  conversationId?: string,
): Promise<import("./types").ChatResponse> {
  const res = await fetch(`${BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, conversation_id: conversationId }),
  });
  return handleResponse<import("./types").ChatResponse>(res);
}

// --- Reminders ---

export async function createReminder(
  documentId: string,
  reminderDate: string,
  createdBy: string,
  note?: string,
): Promise<ContractReminder> {
  const res = await fetch(`${BASE}/api/v1/documents/${documentId}/reminders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reminder_date: reminderDate, created_by: createdBy, note }),
  });
  return handleResponse<ContractReminder>(res);
}

export async function fetchReminders(
  status?: string,
): Promise<{ items: ContractReminder[] }> {
  const url = new URL(`${BASE}/api/v1/reminders`);
  if (status) url.searchParams.set("status", status);
  const res = await fetch(url.toString());
  return handleResponse<{ items: ContractReminder[] }>(res);
}

export async function dismissReminder(
  reminderId: string,
  dismissedBy: string,
): Promise<ContractReminder> {
  const res = await fetch(`${BASE}/api/v1/reminders/${reminderId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: "dismissed", dismissed_by: dismissedBy }),
  });
  return handleResponse<ContractReminder>(res);
}

// --- Ingest ---

export async function ingestSocrata(): Promise<{
  imported: number;
  skipped: number;
  message: string;
}> {
  const res = await fetch(`${BASE}/api/v1/ingest/socrata`, { method: "POST" });
  return handleResponse<{ imported: number; skipped: number; message: string }>(
    res,
  );
}
