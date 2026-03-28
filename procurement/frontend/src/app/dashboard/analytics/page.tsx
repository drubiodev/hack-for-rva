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
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { fetchAnalyticsSummary, fetchRisks, createReminder } from "@/lib/api";
import { analyticsKeys } from "@/lib/queryKeys";
import type { ExpiringContract } from "@/lib/types";
import {
  FileText,
  DollarSign,
  BarChart3,
  CalendarClock,
  AlertTriangle,
  Calendar,
  Check,
} from "lucide-react";

function formatCurrency(amount: number): string {
  if (amount >= 1_000_000) {
    return `$${(amount / 1_000_000).toFixed(1)}M`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function KpiCard({
  title,
  value,
  icon: Icon,
  loading,
  children,
}: {
  title: string;
  value?: string | number;
  icon: React.ComponentType<{ className?: string }>;
  loading: boolean;
  children?: React.ReactNode;
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
        ) : children ? (
          children
        ) : (
          <p className="text-2xl font-bold">{value}</p>
        )}
      </CardContent>
    </Card>
  );
}

function expiryColor(days: number): string {
  if (days < 30) return "text-red-600 dark:text-red-400";
  if (days < 60) return "text-yellow-600 dark:text-yellow-400";
  return "text-green-600 dark:text-green-400";
}

function expiryBadgeVariant(days: number): "destructive" | "secondary" | "outline" {
  if (days < 30) return "destructive";
  if (days < 60) return "secondary";
  return "outline";
}

export default function AnalyticsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [daysFilter, setDaysFilter] = useState<number>(90);
  const [reminderFormId, setReminderFormId] = useState<string | null>(null);
  const [reminderDate, setReminderDate] = useState("");
  const [reminderSetIds, setReminderSetIds] = useState<Set<string>>(new Set());

  const reminderMutation = useMutation({
    mutationFn: (contractId: string) =>
      createReminder(contractId, reminderDate, user?.name ?? "Unknown"),
    onSuccess: (_data, contractId) => {
      queryClient.invalidateQueries({ queryKey: analyticsKeys.all });
      setReminderSetIds((prev) => new Set(prev).add(contractId));
      setReminderFormId(null);
      setReminderDate("");
    },
  });

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: analyticsKeys.summary(),
    queryFn: fetchAnalyticsSummary,
    refetchInterval: 30000,
  });

  const { data: risks, isLoading: risksLoading } = useQuery({
    queryKey: analyticsKeys.risks(daysFilter),
    queryFn: () => fetchRisks(daysFilter),
    refetchInterval: 30000,
  });

  // Top document types from by_type
  const topTypes = summary?.by_type
    ? Object.entries(summary.by_type)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 4)
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground mt-1">
          Procurement risk analysis and document metrics
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Total Documents"
          value={summary?.total_documents ?? 0}
          icon={FileText}
          loading={summaryLoading}
        />
        <KpiCard
          title="By Type"
          icon={BarChart3}
          loading={summaryLoading}
        >
          {topTypes.length > 0 ? (
            <div className="space-y-1">
              {topTypes.map(([type, count]) => (
                <div key={type} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground capitalize">
                    {type.replace("_", " ")}
                  </span>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No data</p>
          )}
        </KpiCard>
        <KpiCard
          title="Total Contract Value"
          value={formatCurrency(summary?.total_contract_value ?? 0)}
          icon={DollarSign}
          loading={summaryLoading}
        />
        <KpiCard
          title="Processed Today"
          value={summary?.documents_processed_today ?? 0}
          icon={CalendarClock}
          loading={summaryLoading}
        />
      </div>

      {/* Risk Summary Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Expiring in 30 days</p>
                {risksLoading ? (
                  <Skeleton className="h-8 w-12 mt-1" />
                ) : (
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {risks?.total_expiring_30 ?? 0}
                  </p>
                )}
              </div>
              <Badge variant="destructive">Critical</Badge>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Expiring in 60 days</p>
                {risksLoading ? (
                  <Skeleton className="h-8 w-12 mt-1" />
                ) : (
                  <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {risks?.total_expiring_60 ?? 0}
                  </p>
                )}
              </div>
              <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                Warning
              </Badge>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Expiring in 90 days</p>
                {risksLoading ? (
                  <Skeleton className="h-8 w-12 mt-1" />
                ) : (
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {risks?.total_expiring_90 ?? 0}
                  </p>
                )}
              </div>
              <Badge variant="outline">Monitor</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Expiring Contracts Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Expiring Contracts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            {[30, 60, 90].map((d) => (
              <Button
                key={d}
                variant={daysFilter === d ? "default" : "outline"}
                size="sm"
                onClick={() => setDaysFilter(d)}
              >
                {d} days
              </Button>
            ))}
          </div>

          {risksLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (risks?.expiring_contracts?.length ?? 0) === 0 ? (
            <p className="text-sm text-muted-foreground py-8 text-center">
              No contracts expiring within {daysFilter} days.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vendor</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead>Expiration</TableHead>
                  <TableHead className="text-right">Days Left</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {risks!.expiring_contracts.map((contract) => (
                  <TableRow
                    key={contract.id}
                    className="cursor-pointer"
                    onClick={() =>
                      router.push(`/dashboard/documents/${contract.id}`)
                    }
                  >
                    <TableCell className="font-medium">
                      {contract.vendor_name}
                    </TableCell>
                    <TableCell className="max-w-[200px] truncate">
                      {contract.title}
                    </TableCell>
                    <TableCell className="text-right">
                      {contract.total_amount != null
                        ? formatCurrency(contract.total_amount)
                        : "N/A"}
                    </TableCell>
                    <TableCell>
                      {new Date(contract.expiration_date).toLocaleDateString(
                        "en-US",
                        { month: "short", day: "numeric", year: "numeric" }
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <span
                        className={`font-semibold ${expiryColor(contract.days_until_expiry)}`}
                      >
                        {contract.days_until_expiry}
                      </span>
                    </TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      {reminderSetIds.has(contract.id) ? (
                        <span className="flex items-center gap-1 text-sm text-green-600">
                          <Check className="h-3 w-3" /> Set
                        </span>
                      ) : reminderFormId === contract.id ? (
                        <div className="flex items-center gap-1">
                          <Input
                            type="date"
                            value={reminderDate}
                            onChange={(e) => setReminderDate(e.target.value)}
                            className="h-8 w-36 text-xs"
                          />
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-8"
                            disabled={!reminderDate || reminderMutation.isPending}
                            onClick={() => reminderMutation.mutate(contract.id)}
                          >
                            Save
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setReminderFormId(contract.id);
                            setReminderDate("");
                          }}
                        >
                          <Calendar className="h-3 w-3 mr-1" />
                          Set Reminder
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Disclaimer */}
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
