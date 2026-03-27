"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/hooks/useAuth";
import { fetchDocument } from "@/lib/api";
import { documentKeys } from "@/lib/queryKeys";
import type {
  DocumentDetail,
  DocumentStatus,
  ValidationResult,
  ActivityEntry,
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
  ChevronDown,
  ChevronRight,
  Clock,
  User,
  Shield,
  Cpu,
  ArrowLeft,
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

// --- Main page ---

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [ocrExpanded, setOcrExpanded] = useState(false);

  const id = params.id;

  const { data: doc, isLoading } = useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => fetchDocument(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status && PROCESSING_STATUSES.includes(status)) return 5000;
      return false;
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

      {/* Processing stepper */}
      <Card>
        <CardContent className="pt-4 pb-3">
          <ProcessingStepper status={doc.status} />
        </CardContent>
      </Card>

      {/* AI disclaimer */}
      <div className="rounded-md border border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950 px-4 py-3">
        <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
          AI-assisted, requires human review.{" "}
          <span className="font-normal text-yellow-700 dark:text-yellow-300">
            Extracted fields may contain errors. Verify all data before making
            decisions.
          </span>
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Extracted Fields */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Extracted Fields
              {fields?.extraction_confidence != null && (
                <Badge variant="outline">
                  {(fields.extraction_confidence * 100).toFixed(0)}% confidence
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fields ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
                <FieldRow label="Title" value={fields.title} />
                <FieldRow label="Document #" value={fields.document_number} />
                <FieldRow label="Vendor" value={fields.vendor_name} />
                <FieldRow label="Department" value={fields.issuing_department} />
                <FieldRow
                  label="Total Amount"
                  value={formatCurrency(fields.total_amount)}
                />
                <FieldRow label="Contract Type" value={fields.contract_type} />
                <FieldRow
                  label="Effective Date"
                  value={formatDate(fields.effective_date)}
                />
                <FieldRow
                  label="Expiration Date"
                  value={formatDate(fields.expiration_date)}
                />
                <FieldRow label="Payment Terms" value={fields.payment_terms} />
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
                />
                {fields.scope_summary && (
                  <div className="sm:col-span-2">
                    <p className="text-muted-foreground text-xs mb-1">
                      Scope Summary
                    </p>
                    <p className="text-sm">{fields.scope_summary}</p>
                  </div>
                )}
              </div>
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
                      {v.resolved && (
                        <Badge variant="outline" className="text-xs">
                          Resolved
                        </Badge>
                      )}
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

      {/* OCR Text Panel (collapsible) */}
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
              <pre className="max-h-96 overflow-auto rounded-md bg-muted p-4 text-xs font-mono whitespace-pre-wrap">
                {doc.ocr_text}
              </pre>
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

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        {doc.status === "extracted" && (
          <Button>Mark as Reviewed</Button>
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
    </div>
  );
}

// --- Field row helper ---

function FieldRow({
  label,
  value,
}: {
  label: string;
  value: string | number | null | undefined;
}) {
  return (
    <div>
      <p className="text-muted-foreground text-xs mb-0.5">{label}</p>
      <p className="font-medium">{value ?? "N/A"}</p>
    </div>
  );
}
