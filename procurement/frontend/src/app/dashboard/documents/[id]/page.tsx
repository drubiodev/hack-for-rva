"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
  fetchAnnotations,
  createAnnotation,
} from "@/lib/api";
import AnnotationLayer from "@/components/AnnotationLayer";
import { documentKeys } from "@/lib/queryKeys";
import type {
  DocumentStatus,
  ValidationSeverity,
  DepartmentCode,
  ComplianceFlag,
  ProcurementMethod,
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
  ChevronDown,
  ChevronRight,
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
  // pending_approval, approved, rejected are all past "analyst_review"
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
                  completed ? "bg-primary" : "bg-muted"
                }`}
              />
            )}
            <div
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium ${
                completed
                  ? "bg-primary/10 text-primary"
                  : active
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
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

// --- Department & Intelligence constants ---

const DEPT_LABELS: Record<DepartmentCode, string> = {
  PUBLIC_WORKS: "Public Works",
  TRANSPORTATION: "Transportation",
  PUBLIC_SAFETY: "Public Safety",
  FINANCE: "Finance",
  INFORMATION_TECHNOLOGY: "Information Technology",
  PLANNING_DEVELOPMENT: "Planning & Development",
  PUBLIC_UTILITIES: "Public Utilities",
  PARKS_RECREATION: "Parks & Recreation",
  HUMAN_RESOURCES: "Human Resources",
  RISK_MANAGEMENT: "Risk Management",
  COMMUNITY_DEVELOPMENT: "Community Development",
  CITY_ASSESSOR: "City Assessor",
  PROCUREMENT: "Procurement",
  OTHER: "Other",
};

const DEPT_COLORS: Record<DepartmentCode, string> = {
  PUBLIC_WORKS: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  TRANSPORTATION: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  PUBLIC_SAFETY: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  FINANCE: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  INFORMATION_TECHNOLOGY: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  PLANNING_DEVELOPMENT: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  PUBLIC_UTILITIES: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200",
  PARKS_RECREATION: "bg-lime-100 text-lime-800 dark:bg-lime-900 dark:text-lime-200",
  HUMAN_RESOURCES: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
  RISK_MANAGEMENT: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  COMMUNITY_DEVELOPMENT: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
  CITY_ASSESSOR: "bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200",
  PROCUREMENT: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
  OTHER: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

const COMPLIANCE_LABELS: Record<ComplianceFlag, string> = {
  MBE_WBE: "MBE/WBE",
  DAVIS_BACON: "Davis-Bacon",
  ADA: "ADA",
  DRUG_FREE_WORKPLACE: "Drug-Free Workplace",
  OSHA: "OSHA",
  VDOT_STANDARDS: "VDOT Standards",
  ENVIRONMENTAL: "Environmental",
  EEO: "EEO",
};

const PROCUREMENT_LABELS: Record<ProcurementMethod, string> = {
  COMPETITIVE_BID: "Competitive Bid",
  COOPERATIVE_PURCHASE: "Cooperative Purchase",
  SOLE_SOURCE: "Sole Source",
  EMERGENCY: "Emergency",
  RFP: "RFP",
  OTHER: "Other",
};

function DeptBadge({ code }: { code: DepartmentCode | null | undefined }) {
  if (!code) return <span className="text-muted-foreground text-sm">--</span>;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${DEPT_COLORS[code] ?? DEPT_COLORS.OTHER}`}
    >
      {DEPT_LABELS[code] ?? code}
    </span>
  );
}

// --- Main page ---

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [ocrExpanded, setOcrExpanded] = useState(false);
  const [intelExpanded, setIntelExpanded] = useState(true);
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [approveComments, setApproveComments] = useState("");
  const [showApproveForm, setShowApproveForm] = useState(false);

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

  const { data: annotations = [] } = useQuery({
    queryKey: ["annotations", id],
    queryFn: () => fetchAnnotations(id),
    enabled: !!id,
  });

  const annotationMutation = useMutation({
    mutationFn: (data: { x: number; y: number; text: string }) => {
      const name = user?.name ?? "Unknown";
      const initials = name
        .split(/\s+/)
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2) || "?";
      return createAnnotation(id, {
        x: data.x,
        y: data.y,
        page: 1,
        text: data.text,
        author: name,
        initials,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["annotations", id] });
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-12 w-full" />
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (!doc) {
    return (
      <div className="space-y-4">
        <p className="text-muted-foreground">Document not found.</p>
        <Button variant="outline" onClick={() => router.push("/dashboard/documents")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Documents
        </Button>
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

  // Group validations by severity
  const errors = validations.filter((v) => v.severity === "error");
  const warnings = validations.filter((v) => v.severity === "warning");
  const infos = validations.filter((v) => v.severity === "info");
  const sortedValidations = [...errors, ...warnings, ...infos];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/dashboard/documents")}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{doc.filename}</h1>
            <p className="text-sm text-muted-foreground">
              {doc.document_type?.toUpperCase() ?? "Unknown type"} &middot;{" "}
              {doc.source}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge
            variant={
              doc.status === "approved"
                ? "default"
                : doc.status === "rejected"
                  ? "destructive"
                  : doc.status === "error"
                    ? "destructive"
                    : "secondary"
            }
          >
            {doc.status.replace("_", " ")}
          </Badge>
        </div>
      </div>

      {/* Processing stepper — only for uploaded documents */}
      {doc.source !== "socrata" && (
        <Card>
          <CardContent className="pt-4 pb-3">
            <ProcessingStepper status={doc.status} />
          </CardContent>
        </Card>
      )}

      {/* Source-appropriate disclaimer */}
      {doc.source === "socrata" ? (
        <div className="rounded-md border border-blue-300 bg-blue-50 dark:border-blue-800 dark:bg-blue-950 px-4 py-3">
          <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
            Official City data source.{" "}
            <span className="font-normal text-blue-700 dark:text-blue-300">
              This record was imported from the City of Richmond Open Data Portal (Socrata).
              Fields reflect the published dataset — no AI extraction was applied.
            </span>
          </p>
        </div>
      ) : (
        <div className="rounded-md border border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950 px-4 py-3">
          <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
            AI-assisted, requires human review.{" "}
            <span className="font-normal text-yellow-700 dark:text-yellow-300">
              Extracted fields may contain errors. Verify all data before making
              decisions.
            </span>
          </p>
        </div>
      )}

      {/* Error state with reprocess button */}
      {doc.status === "error" && doc.error_message && (
        <div className="rounded-md border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
              <p className="text-sm font-medium text-red-800 dark:text-red-200">
                Processing failed
              </p>
            </div>
            {/* Reprocess button for any role on error documents */}
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
          <p className="mt-1 text-sm text-red-700 dark:text-red-300">{doc.error_message}</p>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Extracted Fields */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {doc.source === "socrata" ? "Contract Details" : "Extracted Fields"}
              {doc.source !== "socrata" && fields?.extraction_confidence != null && (
                <Badge variant="outline">
                  {(fields.extraction_confidence * 100).toFixed(0)}% confidence
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fields ? (
              <>
                {/* Per-field confidence legend — only for AI-extracted docs */}
                {doc.source !== "socrata" && fc && (
                  <div className="flex items-center gap-3 mb-4 text-xs text-muted-foreground">
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
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
                  <FieldRow label="Title" value={fields.title} confidence={fc?.title} />
                  <FieldRow label="Document #" value={fields.document_number} />
                  <FieldRow label="Vendor" value={fields.vendor_name} confidence={fc?.vendor_name} />
                  <FieldRow label="Department" value={fields.issuing_department} />
                  <FieldRow
                    label="Total Amount"
                    value={formatCurrency(fields.total_amount)}
                    confidence={fc?.total_amount}
                  />
                  <FieldRow label="Contract Type" value={fields.contract_type} confidence={fc?.contract_type} />
                  <FieldRow
                    label="Effective Date"
                    value={formatDate(fields.effective_date)}
                    confidence={fc?.effective_date}
                  />
                  <FieldRow
                    label="Expiration Date"
                    value={formatDate(fields.expiration_date)}
                    confidence={fc?.expiration_date}
                    critical
                  />
                  <FieldRow label="Payment Terms" value={fields.payment_terms} confidence={fc?.payment_terms} />
                  <FieldRow label="Renewal Clause" value={fields.renewal_clause} />
                  <FieldRow
                    label="Insurance Required"
                    value={
                      fields.insurance_required == null
                        ? "N/A"
                        : fields.insurance_required
                          ? "Yes"
                          : "No"
                    }
                    confidence={fc?.insurance_required}
                  />
                  <FieldRow
                    label="Bond Required"
                    value={
                      fields.bond_required == null
                        ? "N/A"
                        : fields.bond_required
                          ? "Yes"
                          : "No"
                    }
                    confidence={fc?.bond_required}
                  />
                  {/* Expiration date source note */}
                  {expSource && (
                    <div className="sm:col-span-2 rounded-md border border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950 p-2.5">
                      <p className="text-xs font-medium text-blue-800 dark:text-blue-200 mb-0.5">
                        Expiration Date Source
                      </p>
                      <p className="text-xs text-blue-700 dark:text-blue-300">
                        {expSource}
                      </p>
                    </div>
                  )}
                  {fields.scope_summary && (
                    <div className="sm:col-span-2">
                      <p className="text-muted-foreground text-xs mb-1">
                        Scope Summary
                      </p>
                      <p className="text-sm">{fields.scope_summary}</p>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <p className="text-muted-foreground text-sm">
                No extracted fields yet.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Validation Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Validation Alerts
              <div className="flex gap-1">
                {errors.length > 0 && (
                  <Badge variant="destructive">{errors.length}</Badge>
                )}
                {warnings.length > 0 && (
                  <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                    {warnings.length}
                  </Badge>
                )}
                {infos.length > 0 && (
                  <Badge variant="secondary">{infos.length}</Badge>
                )}
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sortedValidations.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                No validation alerts.
              </p>
            ) : (
              <div className="space-y-3">
                {sortedValidations.map((v) => (
                  <div
                    key={v.id}
                    className={`rounded-md border p-3 text-sm ${
                      v.resolved ? "opacity-50" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        {severityBadge(v.severity)}
                        <code className="text-xs text-muted-foreground">
                          {v.rule_code}
                        </code>
                      </div>
                      {v.resolved ? (
                        <Badge variant="outline" className="text-xs">
                          Resolved
                        </Badge>
                      ) : (v.severity === "warning" || v.severity === "info") ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-xs h-6"
                          disabled={resolveWarningMutation.isPending}
                          onClick={() => resolveWarningMutation.mutate(v.id)}
                        >
                          Resolve
                        </Button>
                      ) : null}
                    </div>
                    <p className={v.resolved ? "line-through" : ""}>
                      {v.message}
                    </p>
                    {v.suggestion && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Suggestion: {v.suggestion}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Contract Intelligence Card */}
      <Card>
        <CardHeader
          className="cursor-pointer select-none"
          onClick={() => setIntelExpanded(!intelExpanded)}
        >
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Contract Intelligence
            </div>
            {intelExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </CardTitle>
        </CardHeader>
        {intelExpanded && (
          <CardContent>
            {fields && (fields.primary_department || fields.department_tags?.length || fields.compliance_flags?.length || fields.mbe_wbe_required != null || fields.insurance_general_liability_min != null || fields.procurement_method) ? (
              <div className="grid gap-6 sm:grid-cols-2">
                {/* Department Routing */}
                <div>
                  <h4 className="text-sm font-semibold mb-2">Department Routing</h4>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Primary Department</p>
                      <DeptBadge code={fields.primary_department} />
                      {fields.department_confidence != null && (
                        <span className="ml-2 text-xs text-muted-foreground">
                          ({Math.round(fields.department_confidence * 100)}% confidence)
                        </span>
                      )}
                    </div>
                    {fields.department_tags && fields.department_tags.length > 0 && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Related Departments</p>
                        <div className="flex flex-wrap gap-1">
                          {fields.department_tags.map((dept) => (
                            <DeptBadge key={dept} code={dept} />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Compliance */}
                <div>
                  <h4 className="text-sm font-semibold mb-2">Compliance</h4>
                  <div className="space-y-2">
                    {fields.mbe_wbe_required != null && (
                      <div className="flex items-center gap-2">
                        <Badge variant={fields.mbe_wbe_required ? "default" : "secondary"} className="text-xs">
                          MBE/WBE {fields.mbe_wbe_required ? "Required" : "Not Required"}
                        </Badge>
                      </div>
                    )}
                    {fields.mbe_wbe_details && (
                      <p className="text-xs text-muted-foreground">{fields.mbe_wbe_details}</p>
                    )}
                    {fields.federal_funding != null && (
                      <Badge variant={fields.federal_funding ? "default" : "secondary"} className="text-xs">
                        {fields.federal_funding ? "Federal Funding" : "No Federal Funding"}
                      </Badge>
                    )}
                    {fields.compliance_flags && fields.compliance_flags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {fields.compliance_flags.map((flag) => (
                          <Badge key={flag} variant="outline" className="text-[10px]">
                            {COMPLIANCE_LABELS[flag] ?? flag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Financial Risk */}
                <div>
                  <h4 className="text-sm font-semibold mb-2">Financial Risk</h4>
                  <div className="grid grid-cols-1 gap-1.5 text-sm">
                    {fields.insurance_general_liability_min != null && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">General Liability Min</span>
                        <span className="text-xs font-medium">{formatCurrency(fields.insurance_general_liability_min)}</span>
                      </div>
                    )}
                    {fields.insurance_auto_liability_min != null && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">Auto Liability Min</span>
                        <span className="text-xs font-medium">{formatCurrency(fields.insurance_auto_liability_min)}</span>
                      </div>
                    )}
                    {fields.insurance_professional_liability_min != null && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">Professional Liability Min</span>
                        <span className="text-xs font-medium">{formatCurrency(fields.insurance_professional_liability_min)}</span>
                      </div>
                    )}
                    {fields.workers_comp_required != null && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">Workers Comp</span>
                        <span className="text-xs font-medium">{fields.workers_comp_required ? "Required" : "Not Required"}</span>
                      </div>
                    )}
                    {fields.performance_bond_amount != null && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">Performance Bond</span>
                        <span className="text-xs font-medium">{formatCurrency(fields.performance_bond_amount)}</span>
                      </div>
                    )}
                    {fields.payment_bond_amount != null && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">Payment Bond</span>
                        <span className="text-xs font-medium">{formatCurrency(fields.payment_bond_amount)}</span>
                      </div>
                    )}
                    {fields.liquidated_damages_rate && (
                      <div className="flex justify-between">
                        <span className="text-xs text-muted-foreground">Liquidated Damages</span>
                        <span className="text-xs font-medium">{fields.liquidated_damages_rate}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Procurement */}
                <div>
                  <h4 className="text-sm font-semibold mb-2">Procurement</h4>
                  <div className="space-y-2">
                    {fields.procurement_method && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Method</p>
                        <Badge variant="secondary" className="text-xs">
                          {PROCUREMENT_LABELS[fields.procurement_method] ?? fields.procurement_method}
                        </Badge>
                      </div>
                    )}
                    {fields.cooperative_contract_ref && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Cooperative Contract Ref</p>
                        <p className="text-sm font-medium">{fields.cooperative_contract_ref}</p>
                      </div>
                    )}
                    {fields.prequalification_required != null && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Prequalification</p>
                        <Badge variant={fields.prequalification_required ? "default" : "secondary"} className="text-xs">
                          {fields.prequalification_required ? "Required" : "Not Required"}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">
                Intelligence extraction pending.
              </p>
            )}
          </CardContent>
        )}
      </Card>

      {/* OCR Text Panel (collapsible) with Annotation Layer */}
      <Card>
        <CardHeader
          className="cursor-pointer select-none"
          onClick={() => setOcrExpanded(!ocrExpanded)}
        >
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              OCR Text
              {doc.ocr_confidence != null && (
                <Badge variant="outline">
                  {(doc.ocr_confidence * 100).toFixed(0)}% OCR confidence
                </Badge>
              )}
              {annotations.length > 0 && (
                <Badge variant="secondary" className="text-[10px]">
                  {annotations.length} note{annotations.length !== 1 ? "s" : ""}
                </Badge>
              )}
            </div>
            {ocrExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </CardTitle>
        </CardHeader>
        {ocrExpanded && (
          <CardContent>
            {doc.ocr_text ? (
              <div className="relative max-h-96 overflow-auto rounded-md bg-[#111318]">
                <pre className="p-4 text-xs font-mono whitespace-pre-wrap text-[#94a3b8]">
                  {doc.ocr_text}
                </pre>
                <AnnotationLayer
                  annotations={annotations}
                  onAnnotationCreate={(data) => annotationMutation.mutate(data)}
                />
              </div>
            ) : (
              <p className="text-muted-foreground text-sm">
                No OCR text available.
              </p>
            )}
          </CardContent>
        )}
      </Card>

      {/* Activity Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Activity Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          {activity.length === 0 ? (
            <p className="text-muted-foreground text-sm">No activity yet.</p>
          ) : (
            <div className="space-y-4">
              {activity.map((entry) => (
                <div key={entry.id} className="flex items-start gap-3">
                  <div className="mt-0.5 rounded-full bg-muted p-1.5">
                    {activityIcon(entry.action)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-sm">
                        {entry.actor_name ?? "System"}
                      </span>
                      <Badge
                        variant="outline"
                        className="text-[10px] px-1.5 py-0"
                      >
                        {roleIcon(entry.actor_role)}
                        <span className="ml-1">{entry.actor_role}</span>
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {formatTimestamp(entry.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mt-0.5">
                      {entry.action.replace("_", " ")}
                      {entry.details &&
                        Object.keys(entry.details).length > 0 &&
                        ` — ${JSON.stringify(entry.details)}`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons — role-gated */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-center gap-3">
            {/* Analyst: submit for approval when status is analyst_review */}
            {isAnalyst && doc.status === "analyst_review" && (
              <Button
                onClick={() => submitMutation.mutate()}
                disabled={submitMutation.isPending}
              >
                {submitMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <SendHorizontal className="h-4 w-4 mr-2" />
                )}
                Submit for Approval
              </Button>
            )}

            {/* Supervisor: approve / reject when status is pending_approval */}
            {isSupervisor && doc.status === "pending_approval" && (
              <>
                <Button
                  onClick={() => {
                    setShowApproveForm(!showApproveForm);
                    setShowRejectForm(false);
                  }}
                  disabled={approveMutation.isPending}
                >
                  {approveMutation.isPending ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                  )}
                  Approve
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => {
                    setShowRejectForm(!showRejectForm);
                    setShowApproveForm(false);
                  }}
                  disabled={rejectMutation.isPending}
                >
                  {rejectMutation.isPending ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <XCircle className="h-4 w-4 mr-2" />
                  )}
                  Reject
                </Button>
              </>
            )}

            {/* Supervisor: reprocess at any time */}
            {isSupervisor && (
              <Button
                variant="outline"
                onClick={() => reprocessMutation.mutate()}
                disabled={reprocessMutation.isPending}
              >
                {reprocessMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RotateCw className="h-4 w-4 mr-2" />
                )}
                Reprocess
              </Button>
            )}

            <Button
              variant="outline"
              render={
                <a
                  href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/documents/${doc.id}/export/csv`}
                  download
                />
              }
            >
              Export CSV
            </Button>
          </div>

          {/* Approve form */}
          {showApproveForm && (
            <div className="mt-4 space-y-2">
              <Textarea
                placeholder="Comments (optional)"
                value={approveComments}
                onChange={(e) => setApproveComments(e.target.value)}
              />
              <Button
                onClick={() => approveMutation.mutate()}
                disabled={approveMutation.isPending}
              >
                {approveMutation.isPending ? "Approving..." : "Confirm Approval"}
              </Button>
            </div>
          )}

          {/* Reject form */}
          {showRejectForm && (
            <div className="mt-4 space-y-2">
              <Textarea
                placeholder="Reason for rejection (required)"
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
              />
              <Button
                variant="destructive"
                onClick={() => rejectMutation.mutate()}
                disabled={!rejectReason.trim() || rejectMutation.isPending}
              >
                {rejectMutation.isPending ? "Rejecting..." : "Confirm Rejection"}
              </Button>
            </div>
          )}

          {/* Mutation errors */}
          {(submitMutation.isError || approveMutation.isError || rejectMutation.isError || reprocessMutation.isError) && (
            <div className="mt-3 rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {(submitMutation.error ?? approveMutation.error ?? rejectMutation.error ?? reprocessMutation.error)?.message ?? "An error occurred"}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// --- Field row helper ---

function FieldRow({
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
    <div className={critical && isLow ? "rounded-md border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950 p-2 -m-1" : ""}>
      <div className="flex items-center gap-1.5 mb-0.5">
        <p className="text-muted-foreground text-xs">{label}</p>
        <ConfidenceBadge confidence={confidence} />
      </div>
      <p className="font-medium">{value ?? "N/A"}</p>
      {critical && isLow && (
        <p className="text-[10px] text-red-600 dark:text-red-400 mt-0.5">
          Low confidence — verify against original document
        </p>
      )}
    </div>
  );
}
