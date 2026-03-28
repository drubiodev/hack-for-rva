"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { FileText, Search, ChevronLeft, ChevronRight, ChevronDown } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { fetchDocuments } from "@/lib/api";
import { useChatPanel } from "@/components/ChatPanelContext";
import { documentKeys } from "@/lib/queryKeys";
import type { DocumentStatus, DocumentType, DocumentSource, DepartmentCode } from "@/lib/types";

const DEPT_LABELS: Record<string, string> = {
  PUBLIC_WORKS: "Public Works", TRANSPORTATION: "Transportation",
  PUBLIC_SAFETY: "Public Safety", FINANCE: "Finance",
  INFORMATION_TECHNOLOGY: "IT", PLANNING_DEVELOPMENT: "Planning & Dev",
  PUBLIC_UTILITIES: "Public Utilities", PARKS_RECREATION: "Parks & Rec",
  HUMAN_RESOURCES: "HR", RISK_MANAGEMENT: "Risk Mgmt",
  COMMUNITY_DEVELOPMENT: "Community Dev", CITY_ASSESSOR: "City Assessor",
  PROCUREMENT: "Procurement", OTHER: "Other",
};

const PAGE_SIZE = 20;

const STATUS_OPTIONS: { value: DocumentStatus; label: string }[] = [
  { value: "uploading", label: "Uploading" },
  { value: "ocr_complete", label: "OCR Complete" },
  { value: "classified", label: "Classified" },
  { value: "extracted", label: "Extracted" },
  { value: "analyst_review", label: "Analyst Review" },
  { value: "pending_approval", label: "Pending Approval" },
  { value: "approved", label: "Approved" },
  { value: "rejected", label: "Rejected" },
  { value: "error", label: "Error" },
];

const TYPE_OPTIONS: { value: DocumentType; label: string }[] = [
  { value: "rfp", label: "RFP" },
  { value: "rfq", label: "RFQ" },
  { value: "contract", label: "Contract" },
  { value: "purchase_order", label: "Purchase Order" },
  { value: "invoice", label: "Invoice" },
  { value: "amendment", label: "Amendment" },
  { value: "cooperative", label: "Cooperative" },
  { value: "other", label: "Other" },
];

const SOURCE_OPTIONS: { value: DocumentSource; label: string }[] = [
  { value: "upload", label: "Upload" },
  { value: "socrata", label: "Socrata" },
  { value: "sam_gov", label: "SAM.gov" },
  { value: "eva", label: "eVA" },
];

function formatCompactCurrency(amount: number | null | undefined): string {
  if (amount == null) return "--";
  if (amount >= 1_000_000) {
    return `$${(amount / 1_000_000).toFixed(1)}M`;
  }
  if (amount >= 1_000) {
    return `$${(amount / 1_000).toFixed(0)}K`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function getSourceTag(source: DocumentSource, docType?: DocumentType | null): {
  label: string;
  bg: string;
  text: string;
} {
  // Map source + document_type to colored tags
  if (source === "socrata") {
    return { label: "City", bg: "bg-[#D9F99D]", text: "text-[#365314]" };
  }
  if (source === "upload") {
    if (docType === "rfp") {
      return { label: "GSA", bg: "bg-[#FDE047]", text: "text-[#713F12]" };
    }
    if (docType === "cooperative") {
      return { label: "VITA", bg: "bg-[#BAE6FD]", text: "text-[#0C4A6E]" };
    }
    return { label: "Upload", bg: "bg-[#E7E5E4]", text: "text-[#57534E]" };
  }
  if (source === "sam_gov") {
    return { label: "SAM", bg: "bg-[#FDE047]", text: "text-[#713F12]" };
  }
  if (source === "eva") {
    return { label: "eVA", bg: "bg-[#BAE6FD]", text: "text-[#0C4A6E]" };
  }
  return { label: source, bg: "bg-[#E7E5E4]", text: "text-[#57534E]" };
}

function isExpiringSoon(dateStr: string | null | undefined): "expired" | "warning" | null {
  if (!dateStr) return null;
  const exp = new Date(dateStr);
  const now = new Date();
  const diffDays = Math.floor((exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return "expired";
  if (diffDays <= 30) return "warning";
  return null;
}

export default function DocumentsPage() {
  const router = useRouter();
  const { setActivePage } = useChatPanel();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  useEffect(() => { setActivePage("documents"); }, [setActivePage]);
  const [statusFilter, setStatusFilter] = useState<DocumentStatus | "">("");
  const [typeFilter, setTypeFilter] = useState<DocumentType | "">("");
  const [sourceFilter, setSourceFilter] = useState<DocumentSource | "">("");

  const params = {
    page,
    page_size: PAGE_SIZE,
    search: search || undefined,
    status: statusFilter || undefined,
    document_type: typeFilter || undefined,
    source: sourceFilter || undefined,
  };

  const { data, isLoading, isError, error } = useQuery({
    queryKey: documentKeys.list(params),
    queryFn: () => fetchDocuments(params),
    refetchInterval: 30000,
  });

  const totalPages = data?.total_pages ?? Math.ceil((data?.total ?? 0) / PAGE_SIZE);
  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <h1 className="font-heading text-[32px] font-semibold text-[#0F2537]">
        Unified Portfolio
      </h1>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative w-[400px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#A8A29E]" />
          <input
            type="text"
            placeholder="Search vendors, terms, or departments..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="h-10 w-full rounded-[6px] border border-[#E7E5E4] bg-white pl-9 pr-3 text-sm placeholder-[#A8A29E] outline-none focus:border-[#0F2537] focus:ring-1 focus:ring-[#0F2537]/20"
          />
        </div>

        {/* Source filter */}
        <Select
          value={sourceFilter || undefined}
          onValueChange={(val: string | null) => {
            setSourceFilter(!val || val === "__all__" ? "" : (val as DocumentSource));
            setPage(1);
          }}
        >
          <SelectTrigger className="h-10 w-auto min-w-[120px] gap-2 rounded-[6px] border border-[#E7E5E4] bg-white px-4 text-sm font-medium hover:bg-[#F5F5F4] [&>svg]:hidden">
            <SelectValue placeholder="Source" />
            <ChevronDown className="ml-1 h-3.5 w-3.5 text-[#A8A29E]" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">All Sources</SelectItem>
            {SOURCE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Department (Type) filter */}
        <Select
          value={typeFilter || undefined}
          onValueChange={(val: string | null) => {
            setTypeFilter(!val || val === "__all__" ? "" : (val as DocumentType));
            setPage(1);
          }}
        >
          <SelectTrigger className="h-10 w-auto min-w-[140px] gap-2 rounded-[6px] border border-[#E7E5E4] bg-white px-4 text-sm font-medium hover:bg-[#F5F5F4] [&>svg]:hidden">
            <SelectValue placeholder="Department" />
            <ChevronDown className="ml-1 h-3.5 w-3.5 text-[#A8A29E]" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">All Types</SelectItem>
            {TYPE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Status filter */}
        <Select
          value={statusFilter || undefined}
          onValueChange={(val: string | null) => {
            setStatusFilter(!val || val === "__all__" ? "" : (val as DocumentStatus));
            setPage(1);
          }}
        >
          <SelectTrigger className="h-10 w-auto min-w-[120px] gap-2 rounded-[6px] border border-[#E7E5E4] bg-white px-4 text-sm font-medium hover:bg-[#F5F5F4] [&>svg]:hidden">
            <SelectValue placeholder="Status" />
            <ChevronDown className="ml-1 h-3.5 w-3.5 text-[#A8A29E]" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">All Statuses</SelectItem>
            {STATUS_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Error */}
      {isError && (
        <div className="rounded-[6px] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Failed to load documents:{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </div>
      )}

      {/* Data Table */}
      <div className="overflow-hidden rounded-[12px] border border-[#E7E5E4] bg-white shadow-[0_4px_24px_rgba(15,37,55,0.04)]">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#E7E5E4] bg-[#F5F5F4]">
              <th className="px-5 py-3 text-left font-mono text-[13px] font-medium uppercase tracking-wider text-[#A8A29E]">
                Vendor
              </th>
              <th className="px-5 py-3 text-left font-mono text-[13px] font-medium uppercase tracking-wider text-[#A8A29E]">
                Source
              </th>
              <th className="px-5 py-3 text-left font-mono text-[13px] font-medium uppercase tracking-wider text-[#A8A29E]">
                Department
              </th>
              <th className="px-5 py-3 text-right font-mono text-[13px] font-medium uppercase tracking-wider text-[#A8A29E]">
                Value
              </th>
              <th className="px-5 py-3 text-left font-mono text-[13px] font-medium uppercase tracking-wider text-[#A8A29E]">
                Type
              </th>
              <th className="px-5 py-3 text-left font-mono text-[13px] font-medium uppercase tracking-wider text-[#A8A29E]">
                Expiration
              </th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-[#E7E5E4] last:border-b-0">
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="h-[56px] px-5">
                      <div className="h-4 w-20 animate-pulse rounded bg-[#F5F5F4]" />
                    </td>
                  ))}
                </tr>
              ))
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center text-[#A8A29E]">
                  <FileText className="mx-auto mb-2 h-8 w-8 opacity-50" />
                  No documents found. Try adjusting your filters or upload a new document.
                </td>
              </tr>
            ) : (
              items.map((doc) => {
                const tag = getSourceTag(doc.source, doc.document_type);
                const expiry = isExpiringSoon(doc.expiration_date);

                return (
                  <tr
                    key={doc.id}
                    className="h-[56px] cursor-pointer border-b border-[#E7E5E4] transition-colors last:border-b-0 hover:bg-[#F5F5F4]"
                    onClick={() => router.push(`/dashboard/documents/${doc.id}`)}
                  >
                    {/* Vendor */}
                    <td className="max-w-[220px] truncate px-5 text-[15px] font-medium text-[#292524]">
                      {doc.vendor_name ?? doc.original_filename ?? doc.filename}
                    </td>
                    {/* Source */}
                    <td className="px-5">
                      <span
                        className={`inline-flex h-6 items-center rounded-[4px] px-3 font-mono text-[13px] ${tag.bg} ${tag.text}`}
                      >
                        {tag.label}
                      </span>
                    </td>
                    {/* Department */}
                    <td className="max-w-[180px] truncate px-5 text-[15px] text-[#78716C]">
                      {doc.primary_department ? (DEPT_LABELS[doc.primary_department] ?? doc.primary_department) : "--"}
                    </td>
                    {/* Value */}
                    <td className="px-5 text-right text-[15px] text-[#292524]">
                      {formatCompactCurrency(doc.total_amount)}
                    </td>
                    {/* Type */}
                    <td className="px-5 text-[15px] text-[#78716C] capitalize">
                      {doc.document_type?.replace("_", " ") ?? "--"}
                    </td>
                    {/* Expiration */}
                    <td
                      className={`px-5 text-[15px] ${
                        expiry === "expired"
                          ? "font-semibold text-red-600"
                          : expiry === "warning"
                            ? "font-semibold text-amber-600"
                            : "text-[#292524]"
                      }`}
                    >
                      {formatDate(doc.expiration_date)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-[#E7E5E4] px-5 py-3">
            <p className="text-sm text-[#A8A29E]">
              Page {page} of {totalPages}
              {data?.total ? ` \u00b7 ${data.total} documents` : ""}
            </p>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="inline-flex h-9 items-center gap-1.5 rounded-[6px] border border-[#E7E5E4] bg-white px-3.5 text-sm font-medium text-[#292524] transition-colors hover:bg-[#F5F5F4] disabled:pointer-events-none disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="inline-flex h-9 items-center gap-1.5 rounded-[6px] border border-[#E7E5E4] bg-white px-3.5 text-sm font-medium text-[#292524] transition-colors hover:bg-[#F5F5F4] disabled:pointer-events-none disabled:opacity-40"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
