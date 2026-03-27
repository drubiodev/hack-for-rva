"use client";

import { Badge } from "@/components/ui/badge";
import type { DocumentStatus } from "@/lib/types";

const STATUS_CONFIG: Record<
  DocumentStatus,
  { label: string; variant: "default" | "secondary" | "destructive" | "outline" }
> = {
  uploading: { label: "Uploading", variant: "secondary" },
  ocr_complete: { label: "OCR Complete", variant: "secondary" },
  classified: { label: "Classified", variant: "secondary" },
  extracted: { label: "Extracted", variant: "secondary" },
  analyst_review: { label: "Analyst Review", variant: "outline" },
  pending_approval: { label: "Pending Approval", variant: "outline" },
  approved: { label: "Approved", variant: "default" },
  rejected: { label: "Rejected", variant: "destructive" },
  error: { label: "Error", variant: "destructive" },
};

const STATUS_COLORS: Record<DocumentStatus, string> = {
  uploading: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  ocr_complete: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  classified: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  extracted: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  analyst_review:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  pending_approval:
    "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  approved:
    "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

export function StatusBadge({ status }: { status: DocumentStatus }) {
  const config = STATUS_CONFIG[status];
  const colorClass = STATUS_COLORS[status];

  return (
    <Badge variant={config.variant} className={colorClass}>
      {config.label}
    </Badge>
  );
}
