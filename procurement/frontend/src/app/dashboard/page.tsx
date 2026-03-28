"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import {
  fetchAnalyticsSummary,
  fetchRisks,
  createReminder,
  dismissReminder,
} from "@/lib/api";
import { analyticsKeys } from "@/lib/queryKeys";
import type { ExpiringContract } from "@/lib/types";
import {
  FileText,
  Clock,
  AlertTriangle,
  DollarSign,
  Bell,
  Calendar,
  Check,
} from "lucide-react";

function KpiCard({
  title,
  value,
  icon: Icon,
  loading,
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  loading: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-24" />
        ) : (
          <p className="text-2xl font-bold">{value}</p>
        )}
      </CardContent>
    </Card>
  );
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function expiryBadgeVariant(days: number): "destructive" | "secondary" | "outline" {
  if (days < 30) return "destructive";
  if (days < 60) return "secondary";
  return "outline";
}

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
    mutationFn: () => createReminder(contract.id, date, userName, note || undefined),
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

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [reminderFormId, setReminderFormId] = useState<string | null>(null);
  const [reminderSetIds, setReminderSetIds] = useState<Set<string>>(new Set());

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

  const dismissMutation = useMutation({
    mutationFn: (reminderId: string) =>
      dismissReminder(reminderId, user?.name ?? "Unknown"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.all });
    },
  });

  const pendingReview =
    (summary?.by_status?.["analyst_review"] ?? 0) +
    (summary?.by_status?.["pending_approval"] ?? 0);

  const triggeredReminders = risks?.triggered_reminders ?? [];
  const expiringContracts = risks?.expiring_contracts ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome, {user?.name ?? "User"}
        </h1>
        <p className="text-muted-foreground mt-1">
          Procurement document processing overview
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Total Documents"
          value={summary?.total_documents ?? 0}
          icon={FileText}
          loading={summaryLoading}
        />
        <KpiCard
          title="Pending Review"
          value={pendingReview}
          icon={Clock}
          loading={summaryLoading}
        />
        <KpiCard
          title="Expiring (90 days)"
          value={risks?.total_expiring_90 ?? 0}
          icon={AlertTriangle}
          loading={risksLoading}
        />
        <KpiCard
          title="Total Contract Value"
          value={formatCurrency(summary?.total_contract_value ?? 0)}
          icon={DollarSign}
          loading={summaryLoading}
        />
      </div>

      {/* Triggered Reminders Banner */}
      {triggeredReminders.length > 0 && (
        <Card className="border-yellow-400 bg-yellow-50 dark:bg-yellow-950/30">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-yellow-700 dark:text-yellow-400">
              <Bell className="h-5 w-5" />
              You have {triggeredReminders.length} reminder
              {triggeredReminders.length > 1 ? "s" : ""} due
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
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
                      <span className="text-muted-foreground ml-2">
                        — {reminder.note}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        router.push(`/dashboard/documents/${reminder.document_id}`)
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
          </CardContent>
        </Card>
      )}

      {/* Action Required Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Action Required
          </CardTitle>
        </CardHeader>
        <CardContent>
          {risksLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : expiringContracts.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              No contracts require immediate attention.
            </p>
          ) : (
            <div className="space-y-3">
              {expiringContracts.map((contract) => (
                <div key={contract.id}>
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-sm font-medium truncate">
                        {contract.vendor_name || contract.title}
                      </span>
                      <Badge variant={expiryBadgeVariant(contract.days_until_expiry)}>
                        {contract.days_until_expiry}d
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          router.push(`/dashboard/documents/${contract.id}`)
                        }
                      >
                        Review
                      </Button>
                      {reminderSetIds.has(contract.id) ? (
                        <span className="flex items-center gap-1 text-sm text-green-600">
                          <Check className="h-4 w-4" /> Reminder set
                        </span>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            setReminderFormId(
                              reminderFormId === contract.id ? null : contract.id,
                            )
                          }
                        >
                          <Calendar className="h-4 w-4 mr-1" />
                          Set Reminder
                        </Button>
                      )}
                    </div>
                  </div>
                  {reminderFormId === contract.id && (
                    <ReminderForm
                      contract={contract}
                      userName={user?.name ?? "Unknown"}
                      onSuccess={() => {
                        setReminderFormId(null);
                        setReminderSetIds((prev) => new Set(prev).add(contract.id));
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <p className="text-xs text-muted-foreground text-center">
            AI-assisted, requires human review. This is a decision-support tool
            and does not represent official City procurement records.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
