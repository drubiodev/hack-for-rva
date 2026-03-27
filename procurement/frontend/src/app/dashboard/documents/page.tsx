"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { FileText, Search, ChevronLeft, ChevronRight } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StatusBadge } from "@/components/StatusBadge";
import { fetchDocuments } from "@/lib/api";
import { documentKeys } from "@/lib/queryKeys";
import type { DocumentStatus, DocumentType, DocumentSource } from "@/lib/types";

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

function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return "--";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function DocumentsPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
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
      <h1 className="text-3xl font-bold">Documents</h1>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search documents..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-8"
          />
        </div>
        <Select
          value={statusFilter || null}
          onValueChange={(val) => {
            setStatusFilter((val as DocumentStatus) || "");
            setPage(1);
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={""}>All Statuses</SelectItem>
            {STATUS_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={typeFilter || null}
          onValueChange={(val) => {
            setTypeFilter((val as DocumentType) || "");
            setPage(1);
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={""}>All Types</SelectItem>
            {TYPE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={sourceFilter || null}
          onValueChange={(val) => {
            setSourceFilter((val as DocumentSource) || "");
            setPage(1);
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Sources" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={""}>All Sources</SelectItem>
            {SOURCE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            All Documents{data ? ` (${data.total})` : ""}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isError && (
            <div className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">
              Failed to load documents:{" "}
              {error instanceof Error ? error.message : "Unknown error"}
            </div>
          )}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Filename</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Vendor</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 7 }).map((_, j) => (
                      <TableCell key={j}>
                        <div className="h-4 w-20 animate-pulse rounded bg-muted" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : items.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={7}
                    className="py-8 text-center text-muted-foreground"
                  >
                    <FileText className="mx-auto mb-2 h-8 w-8 opacity-50" />
                    No documents found. Try adjusting your filters or upload a
                    new document.
                  </TableCell>
                </TableRow>
              ) : (
                items.map((doc) => (
                  <TableRow
                    key={doc.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() =>
                      router.push(`/dashboard/documents/${doc.id}`)
                    }
                  >
                    <TableCell className="max-w-[200px] truncate font-medium">
                      {doc.original_filename ?? doc.filename}
                    </TableCell>
                    <TableCell className="capitalize">
                      {doc.document_type?.replace("_", " ") ?? "--"}
                    </TableCell>
                    <TableCell className="max-w-[150px] truncate">
                      {doc.vendor_name ?? "--"}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(doc.total_amount)}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={doc.status} />
                    </TableCell>
                    <TableCell className="capitalize">
                      {doc.source.replace("_", " ")}
                    </TableCell>
                    <TableCell>{formatDate(doc.created_at)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Page {page} of {totalPages}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft className="mr-1 h-4 w-4" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                  <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
