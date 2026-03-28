"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/hooks/useAuth";
import {
  fetchDocument,
  submitForApproval,
  approveDocument,
  rejectDocument,
  reprocessDocument,
  resolveWarning,
} from "@/lib/api";
import { documentKeys } from "@/lib/queryKeys";
import type {
  DocumentStatus,
  ValidationSeverity,
} from "@/lib/types";
import {
  Upload,
  ScanText,
  Tags,
  FileCheck,
  ClipboardCheck,
  Check,
  AlertCircle,
  AlertTriangle,
  Info,
  Clock,
  User,
  Shield,
  Cpu,
  ArrowLeft,
  Loader2,
  RotateCw,
  CheckCircle2,
  XCircle,
  SendHorizontal,
  Sparkles,
  ZoomIn,
  ZoomOut,
  Printer,
  Download,
  FileText,
} from "lucide-react";

// --- Processing stepper ---

const STEPS: { key: string; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "uploading", label: "Uploading", icon: Upload },
  { key: "ocr_complete", label: "OCR", icon: ScanText },
  { key: "classified", label: "Classified", icon: Tags },
  { key: "extracted", label: "Extracted", icon: FileCheck },
  { key: "analyst_review", label: "Review", icon: ClipboardCheck },
];

const STATUS_ORDER: DocumentStatus[] = [
  "uploading",
  "ocr_complete",
  "classified",
  "extracted",
  "analyst_review",
  "pending_approval",
  "approved",
  "rejected",
];

function stepIndex(status: DocumentStatus): number {
  const idx = STATUS_ORDER.indexOf(status);
  return idx >= 0 ? Math.min(idx, STEPS.length - 1) : 0;
}

function ProcessingStepper({ status }: { status: DocumentStatus }) {
  const current = stepIndex(status);

  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-2">
      {STEPS.map((step, i) => {
        const completed = i < current;
        const active = i === current;
        const StepIcon = step.icon;
        return (
          <div key={step.key} className="flex items-center gap-1">
            {i > 0 && (
              <div
                className={`h-0.5 w-6 sm:w-10 ${
                  completed ? "bg-[#1359AE]" : "bg-[#E7E5E4]"
                }`}
              />
            )}
            <div
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium ${
                completed
                  ? "bg-[#1359AE]/10 text-[#1359AE]"
                  : active
                    ? "bg-[#1359AE] text-white"
                    : "bg-[#F3F4F6] text-[#78716C]"
              }`}
            >
              {completed ? (
                <Check className="h-3.5 w-3.5" />
              ) : (
                <StepIcon className="h-3.5 w-3.5" />
              )}
              <span className="hidden sm:inline">{step.label}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// --- Severity helpers ---

function severityBadge(severity: ValidationSeverity) {
  switch (severity) {
    case "error":
      return (
        <Badge variant="destructive">
          <AlertCircle className="h-3 w-3 mr-1" />
          Error
        </Badge>
      );
    case "warning":
      return (
        <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
          <AlertTriangle className="h-3 w-3 mr-1" />
          Warning
        </Badge>
      );
    case "info":
      return (
        <Badge variant="secondary">
          <Info className="h-3 w-3 mr-1" />
          Info
        </Badge>
      );
  }
}

// --- Activity icon ---

function activityIcon(action: string) {
  switch (action) {
    case "uploaded":
      return <Upload className="h-4 w-4" />;
    case "ocr_complete":
      return <ScanText className="h-4 w-4" />;
    case "classified":
      return <Tags className="h-4 w-4" />;
    case "extracted":
      return <FileCheck className="h-4 w-4" />;
    case "approved":
      return <Check className="h-4 w-4 text-green-600" />;
    case "rejected":
      return <AlertCircle className="h-4 w-4 text-red-600" />;
    default:
      return <Clock className="h-4 w-4" />;
  }
}

function roleIcon(role: string) {
  switch (role) {
    case "analyst":
      return <User className="h-3 w-3" />;
    case "supervisor":
      return <Shield className="h-3 w-3" />;
    default:
      return <Cpu className="h-3 w-3" />;
  }
}

// --- Confidence threshold ---
const CONFIDENCE_THRESHOLD = 0.9;

// --- Currency formatter ---

function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(amount);
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function ConfidenceBadge({ confidence }: { confidence: number | undefined }) {
  if (confidence === undefined) return null;
  const pct = Math.round(confidence * 100);
  const isLow = confidence < CONFIDENCE_THRESHOLD;
  return (
    <span
      className={`inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium ${
        isLow
          ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
          : "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      }`}
      title={isLow ? `Below ${CONFIDENCE_THRESHOLD * 100}% threshold — verify manually` : "High confidence"}
    >
      {isLow && <AlertTriangle className="h-2.5 w-2.5 mr-0.5" />}
      {pct}%
    </span>
  );
}

function formatTimestamp(dateStr: string): string {
  return new Date(dateStr).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

// --- Processing states for polling ---

const PROCESSING_STATUSES: DocumentStatus[] = [
  "uploading",
  "ocr_complete",
  "classified",
];

// --- Status tag helpers ---

function statusTagColor(status: DocumentStatus): string {
  switch (status) {
    case "approved":
      return "bg-green-100 text-green-800 border-green-200";
    case "rejected":
    case "error":
      return "bg-red-100 text-red-800 border-red-200";
    case "pending_approval":
      return "bg-amber-100 text-amber-800 border-amber-200";
    case "analyst_review":
      return "bg-blue-100 text-blue-800 border-blue-200";
    default:
      return "bg-[#F3F4F6] text-[#78716C] border-[#E7E5E4]";
  }
}

function sourceTagColor(source: string): string {
  switch (source) {
    case "socrata":
      return "bg-blue-100 text-blue-800 border-blue-200";
    case "upload":
      return "bg-purple-100 text-purple-800 border-purple-200";
    default:
      return "bg-[#F3F4F6] text-[#78716C] border-[#E7E5E4]";
  }
}

function isExpiringSoon(dateStr: string | null | undefined): boolean {
  if (!dateStr) return false;
  const diff = new Date(dateStr).getTime() - Date.now();
  return diff > 0 && diff < 30 * 24 * 60 * 60 * 1000;
}

// --- Main page ---

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [approveComments, setApproveComments] = useState("");
  const [showApproveForm, setShowApproveForm] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);

  const id = params.id;

  const isAnalyst = user?.role === "analyst";
  const isSupervisor = user?.role === "supervisor";

  const { data: doc, isLoading } = useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => fetchDocument(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status && PROCESSING_STATUSES.includes(status)) return 5000;
      return false;
    },
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) });

  const submitMutation = useMutation({
    mutationFn: () => submitForApproval(id, user?.name ?? "Unknown"),
    onSuccess: invalidate,
  });

  const approveMutation = useMutation({
    mutationFn: () =>
      approveDocument(id, user?.name ?? "Unknown", approveComments || undefined),
    onSuccess: () => {
      setShowApproveForm(false);
      setApproveComments("");
      invalidate();
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () =>
      rejectDocument(id, user?.name ?? "Unknown", rejectReason),
    onSuccess: () => {
      setShowRejectForm(false);
      setRejectReason("");
      invalidate();
    },
  });

  const reprocessMutation = useMutation({
    mutationFn: () => reprocessDocument(id, user?.name ?? "Unknown"),
    onSuccess: invalidate,
  });

  const resolveWarningMutation = useMutation({
    mutationFn: (validationId: string) =>
      resolveWarning(id, validationId, user?.name ?? "Unknown"),
    onSuccess: invalidate,
  });

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-56px)] gap-0">
        <div className="w-1/2 p-8 space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
        <div className="w-1/2 bg-[#F3F4F6] p-6">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-[80vh] w-full mt-4" />
        </div>
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-56px)]">
        <div className="text-center space-y-4">
          <p className="text-[#78716C]">Document not found.</p>
          <Button variant="outline" onClick={() => router.push("/dashboard/documents")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>
      </div>
    );
  }

  const fields = doc.extracted_fields;
  const rawExt = fields?.raw_extraction as Record<string, unknown> | undefined;
  const fc = rawExt?.field_confidences as Record<string, number> | undefined;
  const expSource = rawExt?.expiration_date_source as string | undefined;
  const validations = doc.validations ?? [];
  const activity = [...(doc.activity ?? [])].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const errors = validations.filter((v) => v.severity === "error");
  const warnings = validations.filter((v) => v.severity === "warning");
  const infos = validations.filter((v) => v.severity === "info");
  const sortedValidations = [...errors, ...warnings, ...infos];
  const expiring = isExpiringSoon(fields?.expiration_date);

  return (
    <div className="flex flex-col h-[calc(100vh-56px)] -m-6">
      {/* Back bar */}
      <div className="flex items-center h-11 px-4 border-b border-[#E7E5E4] bg-white shrink-0">
        <button
          onClick={() => router.push("/dashboard/documents")}
          className="flex items-center gap-1.5 text-sm text-[#1359AE] hover:text-[#0F2537] transition-colors font-medium"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Portfolio
        </button>
        <span className="flex-1 text-center text-xs font-semibold text-[#78716C] tracking-wide uppercase">
          Secure Workspace
        </span>
        <div className="w-[120px]" />
      </div>

      {/* Split view */}
      <div className="flex-1 flex flex-row overflow-hidden">
        {/* ===== LEFT PANE ===== */}
        <div className="w-1/2 h-full overflow-y-auto border-r border-[#E7E5E4] p-8 bg-white">

          {/* Processing stepper for non-socrata docs */}
          {doc.source !== "socrata" && PROCESSING_STATUSES.includes(doc.status) && (
            <div className="mb-6 rounded-lg border border-[#E7E5E4] p-4 bg-[#FAFAF9]">
              <ProcessingStepper status={doc.status} />
            </div>
          )}

          {/* Error state with reprocess button */}
          {doc.status === "error" && doc.error_message && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <p className="text-sm font-medium text-red-800">Processing failed</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => reprocessMutation.mutate()}
                  disabled={reprocessMutation.isPending}
                >
                  {reprocessMutation.isPending ? (
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                  ) : (
                    <RotateCw className="h-3 w-3 mr-1" />
                  )}
                  Reprocess
                </Button>
              </div>
              <p className="mt-1 text-sm text-red-700">{doc.error_message}</p>
            </div>
          )}

          {/* 1. Header section */}
          <div className="mb-6">
            {/* Source & status tags */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold font-mono border ${sourceTagColor(doc.source)}`}>
                {doc.source === "socrata" ? "Socrata" : doc.source === "upload" ? "Uploaded" : doc.source.toUpperCase()}
              </span>
              <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold font-mono border ${statusTagColor(doc.status)}`}>
                {doc.status.replace("_", " ")}
              </span>
              {doc.document_type && (
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold font-mono border bg-[#F3F4F6] text-[#44403C] border-[#E7E5E4]">
                  {doc.document_type.toUpperCase()}
                </span>
              )}
              {expiring && (
                <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold font-mono border bg-red-100 text-red-800 border-red-200">
                  Expires in 30 Days
                </span>
              )}
            </div>

            {/* Contract title — use vendor as primary heading for Socrata (title is often a long description) */}
            {(() => {
              const title = fields?.title;
              const vendor = fields?.vendor_name;
              const isSocrataLongTitle = doc.source === "socrata" && title && title.length > 80;
              const heading = isSocrataLongTitle && vendor ? vendor : (title ?? doc.filename);
              const subtitle = isSocrataLongTitle ? title : null;
              return (
                <>
                  <h1 className="text-2xl font-semibold text-[#0F2537] mb-1 leading-tight line-clamp-2">
                    {heading}
                  </h1>
                  {subtitle && (
                    <p className="text-sm text-[#78716C] mb-2 line-clamp-2">{subtitle}</p>
                  )}
                </>
              );
            })()}

            {/* Vendor line — show when vendor differs from heading */}
            {fields?.vendor_name && (fields?.title && fields.title.length <= 80 || doc.source !== "socrata") && (
              <div className="flex items-center gap-2 text-[#78716C] mb-4">
                <User className="h-4 w-4" />
                <span className="text-sm font-medium">{fields.vendor_name}</span>
                {fc?.vendor_name !== undefined && (
                  <ConfidenceBadge confidence={fc.vendor_name} />
                )}
              </div>
            )}

            {/* Export button */}
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/documents/${doc.id}/export/csv`}
              download
              className="inline-flex items-center gap-2 rounded-lg bg-[#1359AE] px-4 py-2 text-sm font-medium text-white hover:bg-[#0F2537] transition-colors"
            >
              <Download className="h-4 w-4" />
              Export Brief
            </a>
          </div>

          {/* Source disclaimer */}
          {doc.source === "socrata" ? (
            <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3">
              <p className="text-sm font-medium text-blue-800">
                Official City data source.{" "}
                <span className="font-normal text-blue-700">
                  This record was imported from the City of Richmond Open Data Portal (Socrata).
                  Fields reflect the published dataset — no AI extraction was applied.
                </span>
              </p>
            </div>
          ) : (
            <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3">
              <p className="text-sm font-medium text-yellow-800">
                AI-assisted, requires human review.{" "}
                <span className="font-normal text-yellow-700">
                  Extracted fields may contain errors. Verify all data before making decisions.
                </span>
              </p>
            </div>
          )}

          {/* 2. AI Summary box */}
          {fields?.scope_summary && (
            <div className="mb-6 rounded-lg border border-[#E7E5E4] bg-[#F3F4F6] p-5">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="h-4 w-4 text-[#1359AE]" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#78716C]">
                  AI Summary
                </span>
              </div>
              <p className="text-sm text-[#44403C] leading-relaxed whitespace-pre-line">
                {fields.scope_summary}
              </p>
              {errors.length > 0 && (
                <p className="mt-3 text-sm font-semibold text-red-700">
                  Critical Risk: {errors.length} validation error{errors.length > 1 ? "s" : ""} detected
                </p>
              )}
            </div>
          )}

          {/* 3. Key Extracted Terms grid */}
          {fields && (
            <div className="mb-6">
              <div className="flex items-center justify-between border-b border-[#E7E5E4] pb-2 mb-4">
                <h2 className="text-sm font-semibold text-[#0F2537]">Key Extracted Terms</h2>
                {doc.source !== "socrata" && fields.extraction_confidence != null && (
                  <span className="text-[11px] font-mono text-[#78716C]">
                    {(fields.extraction_confidence * 100).toFixed(0)}% overall confidence
                  </span>
                )}
              </div>

              {/* Per-field confidence legend */}
              {doc.source !== "socrata" && fc && (
                <div className="flex items-center gap-3 mb-4 text-xs text-[#78716C]">
                  <span className="flex items-center gap-1">
                    <span className="inline-block w-2 h-2 rounded-full bg-green-500" />
                    {"\u2265"}{CONFIDENCE_THRESHOLD * 100}% confidence
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="inline-block w-2 h-2 rounded-full bg-red-500" />
                    {"<"}{CONFIDENCE_THRESHOLD * 100}% — verify manually
                  </span>
                </div>
              )}

              <div className="grid grid-cols-2 gap-x-6 gap-y-1">
                <TermCard label="Payment Terms" value={fields.payment_terms} confidence={fc?.payment_terms} />
                <TermCard label="Auto-Renewal" value={fields.renewal_clause} />
                <TermCard
                  label="Insurance Required"
                  value={fields.insurance_required == null ? "N/A" : fields.insurance_required ? "Yes" : "No"}
                  confidence={fc?.insurance_required}
                />
                <TermCard
                  label="Bond Required"
                  value={fields.bond_required == null ? "N/A" : fields.bond_required ? "Yes" : "No"}
                  confidence={fc?.bond_required}
                />
                <TermCard label="Contract Type" value={fields.contract_type} confidence={fc?.contract_type} />
                <TermCard label="Document #" value={fields.document_number} />
                <TermCard
                  label="Total Amount"
                  value={formatCurrency(fields.total_amount)}
                  confidence={fc?.total_amount}
                />
                <TermCard label="Department" value={fields.issuing_department} />
                <TermCard
                  label="Effective Date"
                  value={formatDate(fields.effective_date)}
                  confidence={fc?.effective_date}
                />
                <TermCard
                  label="Expiration Date"
                  value={formatDate(fields.expiration_date)}
                  confidence={fc?.expiration_date}
                  critical
                />
              </div>

              {/* Expiration date source note */}
              {expSource && (
                <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-3">
                  <p className="text-xs font-medium text-blue-800 mb-0.5">
                    Expiration Date Source
                  </p>
                  <p className="text-xs text-blue-700">{expSource}</p>
                </div>
              )}
            </div>
          )}

          {/* 4. Validation Alerts */}
          <div className="mb-6">
            <div className="flex items-center justify-between border-b border-[#E7E5E4] pb-2 mb-4">
              <h2 className="text-sm font-semibold text-[#0F2537]">Validation Alerts</h2>
              <div className="flex gap-1">
                {errors.length > 0 && (
                  <Badge variant="destructive" className="text-[10px] px-1.5">{errors.length}</Badge>
                )}
                {warnings.length > 0 && (
                  <Badge className="bg-yellow-100 text-yellow-800 text-[10px] px-1.5">
                    {warnings.length}
                  </Badge>
                )}
                {infos.length > 0 && (
                  <Badge variant="secondary" className="text-[10px] px-1.5">{infos.length}</Badge>
                )}
              </div>
            </div>

            {sortedValidations.length === 0 ? (
              <p className="text-[#78716C] text-sm">No validation alerts.</p>
            ) : (
              <div className="space-y-2">
                {sortedValidations.map((v) => (
                  <div
                    key={v.id}
                    className={`rounded-lg border border-[#E7E5E4] p-3 text-sm ${
                      v.resolved ? "opacity-50" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        {severityBadge(v.severity)}
                        <code className="text-[10px] text-[#78716C] font-mono">
                          {v.rule_code}
                        </code>
                      </div>
                      {v.resolved ? (
                        <span className="text-[10px] font-mono text-[#78716C] border border-[#E7E5E4] rounded px-1.5 py-0.5">
                          Resolved
                        </span>
                      ) : (v.severity === "warning" || v.severity === "info") ? (
                        <button
                          className="text-[11px] font-medium text-[#1359AE] hover:text-[#0F2537] transition-colors disabled:opacity-50"
                          disabled={resolveWarningMutation.isPending}
                          onClick={() => resolveWarningMutation.mutate(v.id)}
                        >
                          Resolve
                        </button>
                      ) : null}
                    </div>
                    <p className={`text-[#44403C] ${v.resolved ? "line-through" : ""}`}>
                      {v.message}
                    </p>
                    {v.suggestion && (
                      <p className="text-xs text-[#78716C] mt-1">
                        Suggestion: {v.suggestion}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 5. Activity Timeline */}
          {activity.length > 0 && (
            <div className="mb-6">
              <div className="border-b border-[#E7E5E4] pb-2 mb-4">
                <h2 className="text-sm font-semibold text-[#0F2537]">Activity Timeline</h2>
              </div>
              <div className="space-y-3">
                {activity.map((entry) => (
                  <div key={entry.id} className="flex items-start gap-3">
                    <div className="mt-0.5 rounded-full bg-[#F3F4F6] p-1.5">
                      {activityIcon(entry.action)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-sm text-[#0F2537]">
                          {entry.actor_name ?? "System"}
                        </span>
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono text-[#78716C] border border-[#E7E5E4] rounded px-1.5 py-0">
                          {roleIcon(entry.actor_role)}
                          {entry.actor_role}
                        </span>
                        <span className="text-[11px] text-[#78716C]">
                          {formatTimestamp(entry.created_at)}
                        </span>
                      </div>
                      <p className="text-sm text-[#78716C] mt-0.5">
                        {entry.action.replace("_", " ")}
                        {entry.details &&
                          Object.keys(entry.details).length > 0 &&
                          ` — ${JSON.stringify(entry.details)}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 6. Action Buttons */}
          <div className="border-t border-[#E7E5E4] pt-6">
            <div className="flex flex-wrap items-center gap-3">
              {/* Analyst: submit for approval when status is analyst_review */}
              {isAnalyst && doc.status === "analyst_review" && (
                <button
                  onClick={() => submitMutation.mutate()}
                  disabled={submitMutation.isPending}
                  className="inline-flex items-center gap-2 rounded-lg bg-[#1359AE] px-4 py-2 text-sm font-medium text-white hover:bg-[#0F2537] transition-colors disabled:opacity-50"
                >
                  {submitMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <SendHorizontal className="h-4 w-4" />
                  )}
                  Submit for Approval
                </button>
              )}

              {/* Supervisor: approve / reject when status is pending_approval */}
              {isSupervisor && doc.status === "pending_approval" && (
                <>
                  <button
                    onClick={() => {
                      setShowApproveForm(!showApproveForm);
                      setShowRejectForm(false);
                    }}
                    disabled={approveMutation.isPending}
                    className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 transition-colors disabled:opacity-50"
                  >
                    {approveMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle2 className="h-4 w-4" />
                    )}
                    Approve
                  </button>
                  <button
                    onClick={() => {
                      setShowRejectForm(!showRejectForm);
                      setShowApproveForm(false);
                    }}
                    disabled={rejectMutation.isPending}
                    className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors disabled:opacity-50"
                  >
                    {rejectMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <XCircle className="h-4 w-4" />
                    )}
                    Reject
                  </button>
                </>
              )}

              {/* Supervisor: reprocess at any time */}
              {isSupervisor && (
                <button
                  onClick={() => reprocessMutation.mutate()}
                  disabled={reprocessMutation.isPending}
                  className="inline-flex items-center gap-2 rounded-lg border border-[#E7E5E4] bg-white px-4 py-2 text-sm font-medium text-[#44403C] hover:bg-[#F3F4F6] transition-colors disabled:opacity-50"
                >
                  {reprocessMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RotateCw className="h-4 w-4" />
                  )}
                  Reprocess
                </button>
              )}
            </div>

            {/* Approve form */}
            {showApproveForm && (
              <div className="mt-4 space-y-2">
                <Textarea
                  placeholder="Comments (optional)"
                  value={approveComments}
                  onChange={(e) => setApproveComments(e.target.value)}
                  className="border-[#E7E5E4]"
                />
                <button
                  onClick={() => approveMutation.mutate()}
                  disabled={approveMutation.isPending}
                  className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  {approveMutation.isPending ? "Approving..." : "Confirm Approval"}
                </button>
              </div>
            )}

            {/* Reject form */}
            {showRejectForm && (
              <div className="mt-4 space-y-2">
                <Textarea
                  placeholder="Reason for rejection (required)"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  className="border-[#E7E5E4]"
                />
                <button
                  onClick={() => rejectMutation.mutate()}
                  disabled={!rejectReason.trim() || rejectMutation.isPending}
                  className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {rejectMutation.isPending ? "Rejecting..." : "Confirm Rejection"}
                </button>
              </div>
            )}

            {/* Mutation errors */}
            {(submitMutation.isError || approveMutation.isError || rejectMutation.isError || reprocessMutation.isError) && (
              <div className="mt-3 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800">
                {(submitMutation.error ?? approveMutation.error ?? rejectMutation.error ?? reprocessMutation.error)?.message ?? "An error occurred"}
              </div>
            )}
          </div>
        </div>

        {/* ===== RIGHT PANE — Document Viewer ===== */}
        <div className="w-1/2 h-full bg-[#F3F4F6] flex flex-col">
          {/* PDF toolbar */}
          <div className="flex items-center justify-between h-10 px-4 bg-[#1F2937] shrink-0">
            <div className="flex items-center gap-2">
              <FileText className="h-3.5 w-3.5 text-[#9CA3AF]" />
              <span className="text-[12px] font-mono text-[#D1D5DB] truncate max-w-[200px]">
                {doc.filename}
              </span>
              {doc.ocr_confidence != null && (
                <span className="text-[10px] font-mono text-[#9CA3AF] ml-2">
                  OCR {(doc.ocr_confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}
                className="p-1 text-[#9CA3AF] hover:text-white transition-colors"
                title="Zoom out"
              >
                <ZoomOut className="h-3.5 w-3.5" />
              </button>
              <span className="text-[11px] font-mono text-[#9CA3AF] w-10 text-center">
                {zoomLevel}%
              </span>
              <button
                onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}
                className="p-1 text-[#9CA3AF] hover:text-white transition-colors"
                title="Zoom in"
              >
                <ZoomIn className="h-3.5 w-3.5" />
              </button>
              <div className="w-px h-4 bg-[#4B5563] mx-1" />
              <button
                onClick={() => window.print()}
                className="p-1 text-[#9CA3AF] hover:text-white transition-colors"
                title="Print"
              >
                <Printer className="h-3.5 w-3.5" />
              </button>
              {doc.blob_url && (
                <a
                  href={doc.blob_url}
                  download
                  className="p-1 text-[#9CA3AF] hover:text-white transition-colors"
                  title="Download original"
                >
                  <Download className="h-3.5 w-3.5" />
                </a>
              )}
            </div>
          </div>

          {/* Document content area */}
          <div className="flex-1 overflow-auto p-6">
            {doc.ocr_text ? (
              <div
                className="mx-auto bg-white shadow-lg rounded-sm border border-[#E7E5E4]"
                style={{
                  maxWidth: "800px",
                  padding: `${Math.round(48 * zoomLevel / 100)}px ${Math.round(56 * zoomLevel / 100)}px`,
                  fontSize: `${Math.round(11 * zoomLevel / 100)}px`,
                }}
              >
                <pre
                  className="whitespace-pre-wrap leading-relaxed text-[#1C1917]"
                  style={{
                    fontFamily: "Georgia, 'Times New Roman', serif",
                    fontSize: `${Math.round(11 * zoomLevel / 100)}px`,
                  }}
                >
                  {doc.ocr_text}
                </pre>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-[#78716C]">
                <FileText className="h-16 w-16 mb-4 text-[#D6D3D1]" />
                <p className="text-sm font-medium mb-1">No document preview available</p>
                <p className="text-xs">
                  {PROCESSING_STATUSES.includes(doc.status)
                    ? "Document is still being processed..."
                    : doc.source === "socrata"
                      ? "Socrata records do not include document text."
                      : "OCR text was not generated for this document."}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Term card helper for the 2-column grid ---

function TermCard({
  label,
  value,
  confidence,
  critical,
}: {
  label: string;
  value: string | number | null | undefined;
  confidence?: number;
  critical?: boolean;
}) {
  const isLow = confidence !== undefined && confidence < CONFIDENCE_THRESHOLD;
  return (
    <div
      className={`group rounded-lg p-3 transition-colors hover:bg-[#F3F4F6] ${
        critical && isLow
          ? "border border-red-200 bg-red-50"
          : "border border-transparent"
      }`}
    >
      <div className="flex items-center gap-1.5 mb-0.5">
        <p className="text-[11px] font-mono uppercase tracking-wider text-[#78716C]">
          {label}
        </p>
        <ConfidenceBadge confidence={confidence} />
      </div>
      <p className="text-[15px] font-medium text-[#0F2537]">{value ?? "N/A"}</p>
      {critical && isLow && (
        <p className="text-[10px] text-red-600 mt-0.5">
          Low confidence — verify against original document
        </p>
      )}
    </div>
  );
}
