"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import { useChatPanel } from "@/components/ChatPanelContext";
import {
  fetchAnalyticsSummary,
  fetchRisks,
  createReminder,
  dismissReminder,
  fetchComplianceGaps,
  fetchVendorConcentration,
  fetchSoleSourceReview,
} from "@/lib/api";
import { analyticsKeys } from "@/lib/queryKeys";
import type { ExpiringContract } from "@/lib/types";
import {
  Bell,
  Calendar,
  Check,
  Timer,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  ShieldAlert,
  Users,
  FileWarning,
  MessageSquare,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatCurrency(amount: number): string {
  if (amount >= 1_000_000_000) {
    return `$${(amount / 1_000_000_000).toFixed(1)}B`;
  }
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

function formatFullCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

const CARD =
  "bg-white rounded-[12px] border border-[#E7E5E4] shadow-[0_4px_24px_rgba(15,37,55,0.04)]";

/* ------------------------------------------------------------------ */
/*  Source tag — derived from contract title/description                */
/* ------------------------------------------------------------------ */

const SOURCE_COLORS: Record<string, string> = {
  VITA: "bg-[#BAE6FD] text-[#0F2537]",
  GSA: "bg-[#FDE047] text-[#0F2537]",
  City: "bg-[#D9F99D] text-[#0F2537]",
};

function inferSource(contract: ExpiringContract): string {
  const text = `${contract.title ?? ""} ${contract.vendor_name ?? ""}`.toLowerCase();
  if (text.includes("gsa") || text.includes("federal") || text.includes("schedule")) return "GSA";
  if (text.includes("vita") || text.includes("cooperative") || text.includes("state contract")) return "VITA";
  return "City";
}

/* ------------------------------------------------------------------ */
/*  Reminder Form (kept from existing code)                            */
/* ------------------------------------------------------------------ */

function ReminderForm({
  contract,
  userName,
  onSuccess,
}: {
  contract: ExpiringContract;
  userName: string;
  onSuccess: () => void;
}) {
  const queryClient = useQueryClient();
  const [date, setDate] = useState("");
  const [note, setNote] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      createReminder(contract.id, date, userName, note || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.all });
      onSuccess();
    },
  });

  return (
    <div className="flex items-center gap-2 mt-2">
      <Input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
        className="w-40"
      />
      <Input
        placeholder="Note (optional)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        className="w-48"
      />
      <Button
        size="sm"
        disabled={!date || mutation.isPending}
        onClick={() => mutation.mutate()}
      >
        {mutation.isPending ? "Saving..." : "Save"}
      </Button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Dashboard Page                                                     */
/* ------------------------------------------------------------------ */

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { openWithQuery, setActivePage } = useChatPanel();
  const [reminderFormId, setReminderFormId] = useState<string | null>(null);
  const [reminderSetIds, setReminderSetIds] = useState<Set<string>>(new Set());

  useEffect(() => { setActivePage("dashboard"); }, [setActivePage]);

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: analyticsKeys.summary(),
    queryFn: fetchAnalyticsSummary,
    retry: false,
  });

  const { data: risks, isLoading: risksLoading } = useQuery({
    queryKey: analyticsKeys.risks(90),
    queryFn: () => fetchRisks(90),
    retry: false,
  });

  const { data: complianceData } = useQuery({
    queryKey: ["intelligence", "compliance-gaps"],
    queryFn: fetchComplianceGaps,
    retry: false,
    refetchInterval: 30_000,
  });

  const { data: vendorData } = useQuery({
    queryKey: ["intelligence", "vendor-concentration"],
    queryFn: fetchVendorConcentration,
    retry: false,
    refetchInterval: 30_000,
  });

  const { data: soleSourceData } = useQuery({
    queryKey: ["intelligence", "sole-source"],
    queryFn: () => fetchSoleSourceReview(50000),
    retry: false,
    refetchInterval: 30_000,
  });

  const dismissMutation = useMutation({
    mutationFn: (reminderId: string) =>
      dismissReminder(reminderId, user?.name ?? "Unknown"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.all });
    },
  });

  const triggeredReminders = risks?.triggered_reminders ?? [];
  const expiringContracts = risks?.expiring_contracts ?? [];
  const totalActiveValue = summary?.total_contract_value ?? 0;
  const expiring90 = risks?.total_expiring_90 ?? 0;
  const totalDocs = summary?.total_documents ?? 0;

  return (
    <div className="space-y-6">
      {/* ---- Triggered Reminders Banner (preserved) ---- */}
      {triggeredReminders.length > 0 && (
        <div
          className={`${CARD} border-yellow-400 bg-yellow-50`}
        >
          <div className="px-5 pt-4 pb-2">
            <h3 className="flex items-center gap-2 font-heading text-yellow-700 font-semibold">
              <Bell className="h-5 w-5" />
              You have {triggeredReminders.length} reminder
              {triggeredReminders.length > 1 ? "s" : ""} due
            </h3>
          </div>
          <div className="px-5 pb-4 space-y-3">
            {triggeredReminders.map((reminder) => (
              <div
                key={reminder.id}
                className="flex items-center justify-between gap-4"
              >
                <div className="text-sm">
                  <span className="font-medium">
                    {reminder.vendor_name ?? reminder.title ?? "Contract"}
                  </span>
                  {reminder.note && (
                    <span className="text-[#A8A29E] ml-2">
                      — {reminder.note}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      router.push(
                        `/dashboard/documents/${reminder.document_id}`,
                      )
                    }
                  >
                    Review
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={dismissMutation.isPending}
                    onClick={() => dismissMutation.mutate(reminder.id)}
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ---- Top Row — 3 Metric Cards ---- */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Total Active Value */}
        <div className={`${CARD} p-5 h-[140px] flex flex-col justify-between`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[#A8A29E]">
              Total Active Value
            </span>
            <DollarSign className="h-5 w-5 text-[#A8A29E]" />
          </div>
          {summaryLoading ? (
            <Skeleton className="h-10 w-32" />
          ) : (
            <div>
              <p
                className="text-3xl font-heading font-bold text-[#0F2537] tracking-tight"
                title={formatFullCurrency(totalActiveValue)}
              >
                {formatCurrency(totalActiveValue)}
              </p>
              <p className="text-xs text-[#A8A29E] mt-0.5">
                Across {totalDocs} active contracts
              </p>
            </div>
          )}
        </div>

        {/* Expiring (90 days) */}
        <div
          className={`${CARD} p-5 h-[140px] flex flex-col justify-between relative overflow-hidden`}
        >
          {/* red corner accent */}
          <div className="absolute top-0 right-0 w-20 h-20 bg-red-50 rounded-bl-[40px] -z-0" />
          <div className="flex items-center justify-between relative z-10">
            <span className="text-sm font-medium text-[#A8A29E]">
              Expiring (90 days)
            </span>
            <AlertTriangle className="h-5 w-5 text-[#DC2626]" />
          </div>
          {risksLoading ? (
            <Skeleton className="h-10 w-16" />
          ) : (
            <div className="relative z-10">
              <p className="text-3xl font-heading font-bold text-[#DC2626] tracking-tight">
                {expiring90}
              </p>
              <p className="text-xs text-[#A8A29E] mt-0.5">
                Requires immediate review
              </p>
            </div>
          )}
        </div>

        {/* Active Contracts */}
        <div className={`${CARD} p-5 h-[140px] flex flex-col justify-between`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[#A8A29E]">
              Active Contracts
            </span>
            <TrendingUp className="h-5 w-5 text-[#16A34A]" />
          </div>
          {summaryLoading ? (
            <Skeleton className="h-10 w-16" />
          ) : (
            <div>
              <p className="text-3xl font-heading font-bold text-[#0F2537] tracking-tight">
                {totalDocs.toLocaleString()}
              </p>
              <p className="text-xs text-[#A8A29E] mt-0.5">
                From City of Richmond Socrata data
              </p>
            </div>
          )}
        </div>
      </div>

      {/* ---- Intelligence Cards ---- */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* Compliance Gaps */}
        <button
          onClick={() => openWithQuery("Which contracts have compliance gaps?")}
          className={`${CARD} p-5 text-left hover:shadow-md transition-shadow group`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">
              <ShieldAlert className="h-4.5 w-4.5 text-[#DC2626]" />
            </div>
            <MessageSquare className="h-3.5 w-3.5 text-[#A8A29E] opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="text-2xl font-heading font-bold text-[#0F2537] tracking-tight">
            {complianceData?.count ?? <Skeleton className="h-7 w-8 inline-block" />}
          </div>
          <p className="text-sm font-medium text-[#292524] mt-0.5">Compliance Gaps</p>
          <p className="text-xs text-[#A8A29E] mt-1">
            High-value contracts with missing required fields
          </p>
        </button>

        {/* Vendor Concentration */}
        <button
          onClick={() => openWithQuery("Which vendors have the highest contract concentration?")}
          className={`${CARD} p-5 text-left hover:shadow-md transition-shadow group`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50">
              <Users className="h-4.5 w-4.5 text-[#D97706]" />
            </div>
            <MessageSquare className="h-3.5 w-3.5 text-[#A8A29E] opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="text-2xl font-heading font-bold text-[#0F2537] tracking-tight">
            {vendorData?.count ?? <Skeleton className="h-7 w-8 inline-block" />}
          </div>
          <p className="text-sm font-medium text-[#292524] mt-0.5">Vendor Concentration</p>
          <p className="text-xs text-[#A8A29E] mt-1">
            Vendors with multiple contracts — concentration risk
          </p>
        </button>

        {/* Sole-Source Review */}
        <button
          onClick={() => openWithQuery("Show me sole-source contracts over $50K that need review")}
          className={`${CARD} p-5 text-left hover:shadow-md transition-shadow group`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-50">
              <FileWarning className="h-4.5 w-4.5 text-[#7C3AED]" />
            </div>
            <MessageSquare className="h-3.5 w-3.5 text-[#A8A29E] opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="text-2xl font-heading font-bold text-[#0F2537] tracking-tight">
            {soleSourceData?.count ?? <Skeleton className="h-7 w-8 inline-block" />}
          </div>
          <p className="text-sm font-medium text-[#292524] mt-0.5">Sole-Source Review</p>
          <p className="text-xs text-[#A8A29E] mt-1">
            Sole-source contracts over $50K requiring justification
          </p>
        </button>
      </div>

      {/* ---- Main Grid — 60/40 split ---- */}
      <div className="grid gap-4 lg:grid-cols-12">
        {/* Left: Urgent Expirations */}
        <div className={`${CARD} lg:col-span-7 flex flex-col`}>
          {/* Red-tinted header */}
          <div className="flex items-center justify-between px-5 py-3 bg-[#FEF2F2] rounded-t-[12px] border-b border-[#E7E5E4]">
            <div className="flex items-center gap-2">
              <Timer className="h-4 w-4 text-[#991B1B]" />
              <h3 className="text-sm font-heading font-semibold text-[#991B1B]">
                Urgent Expirations
              </h3>
            </div>
            <button
              onClick={() => router.push("/dashboard/documents")}
              className="text-xs font-medium text-[#991B1B] hover:underline"
            >
              View All
            </button>
          </div>

          {/* Table */}
          <div className="flex-1 px-5 py-3">
            {risksLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : expiringContracts.length === 0 ? (
              <p className="text-sm text-[#A8A29E] py-8 text-center">
                No contracts require immediate attention.
              </p>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="text-left text-xs text-[#A8A29E] border-b border-[#E7E5E4]">
                    <th className="pb-2 font-medium">Contract / Vendor</th>
                    <th className="pb-2 font-medium">Source</th>
                    <th className="pb-2 font-medium text-right">Status</th>
                    <th className="pb-2 w-10" />
                  </tr>
                </thead>
                <tbody>
                  {expiringContracts.map((contract, idx) => {
                    const source = inferSource(contract);
                    const daysColor =
                      contract.days_until_expiry < 20
                        ? "text-[#DC2626]"
                        : contract.days_until_expiry < 40
                          ? "text-[#D97706]"
                          : "text-[#A8A29E]";

                    return (
                      <tr
                        key={contract.id}
                        className="border-b border-[#E7E5E4] last:border-0 hover:bg-[#F5F5F4] cursor-pointer transition-colors"
                        onClick={() =>
                          router.push(`/dashboard/documents/${contract.id}`)
                        }
                      >
                        <td className="py-3 pr-3">
                          <div className="text-sm font-medium text-[#292524] truncate max-w-[260px]">
                            {contract.vendor_name || contract.title}
                          </div>
                          {contract.vendor_name && contract.title && (
                            <div className="text-xs text-[#A8A29E] truncate max-w-[260px]">
                              {contract.title}
                            </div>
                          )}
                        </td>
                        <td className="py-3 pr-3">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[13px] font-mono ${SOURCE_COLORS[source]}`}
                          >
                            {source}
                          </span>
                        </td>
                        <td
                          className={`py-3 text-right text-sm font-semibold ${daysColor}`}
                        >
                          {contract.days_until_expiry}d left
                        </td>
                        <td className="py-3 text-right">
                          {reminderSetIds.has(contract.id) ? (
                            <span className="flex items-center gap-1 text-xs text-green-600">
                              <Check className="h-3 w-3" />
                            </span>
                          ) : (
                            <button
                              className="text-[#A8A29E] hover:text-[#0F2537] transition-colors"
                              title="Set Reminder"
                              onClick={(e) => {
                                e.stopPropagation();
                                setReminderFormId(
                                  reminderFormId === contract.id
                                    ? null
                                    : contract.id,
                                );
                              }}
                            >
                              <Calendar className="h-4 w-4" />
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}

            {/* Inline reminder form */}
            {reminderFormId &&
              expiringContracts.find((c) => c.id === reminderFormId) && (
                <div className="mt-2 pb-2">
                  <ReminderForm
                    contract={
                      expiringContracts.find(
                        (c) => c.id === reminderFormId,
                      )!
                    }
                    userName={user?.name ?? "Unknown"}
                    onSuccess={() => {
                      setReminderSetIds(
                        (prev) => new Set(prev).add(reminderFormId),
                      );
                      setReminderFormId(null);
                    }}
                  />
                </div>
              )}
          </div>
        </div>

        {/* Right: Contract Insights */}
        <div className={`${CARD} lg:col-span-5 flex flex-col`}>
          {/* Header */}
          <div className="flex items-center gap-2 px-5 py-3 border-b border-[#E7E5E4]">
            <Sparkles className="h-4 w-4 text-[#818CF8]" />
            <h3 className="text-sm font-heading font-semibold text-[#0F2537]">
              Contract Insights
            </h3>
          </div>

          {/* Insights from real data */}
          <div className="h-[500px] overflow-y-auto px-5 py-4">
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-[7px] top-3 bottom-3 w-px bg-[#E7E5E4]" />

              <div className="space-y-6">
                {/* Expiry insight */}
                <div className="relative flex gap-4 pl-0">
                  <div className="relative z-10 mt-1 h-[15px] w-[15px] rounded-full bg-[#DC2626] shrink-0" />
                  <div className="flex-1 min-w-0">
                    <span className="text-[11px] font-mono text-[#A8A29E]">Expiring contracts</span>
                    <div className="mt-1">
                      <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-red-100 text-red-700">
                        Risk Alert
                      </span>
                    </div>
                    <p className="text-sm text-[#292524] mt-1.5 leading-relaxed">
                      {risksLoading ? "Loading..." : (
                        <>
                          <strong>{risks?.total_expiring_30 ?? 0}</strong> contracts expire within 30 days,{" "}
                          <strong>{risks?.total_expiring_60 ?? 0}</strong> within 60 days, and{" "}
                          <strong>{risks?.total_expiring_90 ?? 0}</strong> within 90 days.
                          Review and renew high-value contracts before deadlines.
                        </>
                      )}
                    </p>
                    <button
                      className="text-xs font-medium text-[#818CF8] hover:underline mt-1.5"
                      onClick={() => router.push("/dashboard/analytics")}
                    >
                      View Analytics &rarr;
                    </button>
                  </div>
                </div>

                {/* Portfolio breakdown insight */}
                <div className="relative flex gap-4 pl-0">
                  <div className="relative z-10 mt-1 h-[15px] w-[15px] rounded-full bg-[#818CF8] shrink-0" />
                  <div className="flex-1 min-w-0">
                    <span className="text-[11px] font-mono text-[#A8A29E]">Portfolio breakdown</span>
                    <div className="mt-1">
                      <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-purple-100 text-purple-700">
                        Analysis
                      </span>
                    </div>
                    <p className="text-sm text-[#292524] mt-1.5 leading-relaxed">
                      {summaryLoading ? "Loading..." : (
                        <>
                          Portfolio of <strong>{totalDocs.toLocaleString()}</strong> contracts
                          totaling <strong>{formatCurrency(totalActiveValue)}</strong>.
                          {summary?.by_status && Object.keys(summary.by_status).length > 0 && (
                            <> Status breakdown:{" "}
                              {Object.entries(summary.by_status).map(([status, count], i) => (
                                <span key={status}>
                                  {i > 0 && ", "}
                                  {count} {status}
                                </span>
                              ))}
                              .
                            </>
                          )}
                        </>
                      )}
                    </p>
                    <button
                      className="text-xs font-medium text-[#818CF8] hover:underline mt-1.5"
                      onClick={() => router.push("/dashboard/documents")}
                    >
                      View Portfolio &rarr;
                    </button>
                  </div>
                </div>

                {/* Top expiring contract insight */}
                {expiringContracts.length > 0 && (
                  <div className="relative flex gap-4 pl-0">
                    <div className="relative z-10 mt-1 h-[15px] w-[15px] rounded-full bg-[#D97706] shrink-0" />
                    <div className="flex-1 min-w-0">
                      <span className="text-[11px] font-mono text-[#A8A29E]">Highest-value expiration</span>
                      <div className="mt-1">
                        <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-amber-100 text-amber-700">
                          Priority
                        </span>
                      </div>
                      {(() => {
                        const top = [...expiringContracts]
                          .filter((c) => c.total_amount != null)
                          .sort((a, b) => (b.total_amount ?? 0) - (a.total_amount ?? 0))[0];
                        if (!top) return null;
                        return (
                          <p className="text-sm text-[#292524] mt-1.5 leading-relaxed">
                            <strong>{top.vendor_name}</strong> contract valued at{" "}
                            <strong>{formatCurrency(top.total_amount ?? 0)}</strong> expires in{" "}
                            <strong>{top.days_until_expiry} days</strong>.
                            This is the highest-value contract requiring renewal action.
                          </p>
                        );
                      })()}
                      <button
                        className="text-xs font-medium text-[#818CF8] hover:underline mt-1.5"
                        onClick={() => router.push(`/dashboard/documents/${expiringContracts[0].id}`)}
                      >
                        Review Contract &rarr;
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ---- Disclaimer ---- */}
      <div className={`${CARD} px-5 py-4`}>
        <p className="text-xs text-[#A8A29E] text-center">
          AI-assisted, requires human review. This is a decision-support tool
          and does not represent official City procurement records.
        </p>
      </div>
    </div>
  );
}
