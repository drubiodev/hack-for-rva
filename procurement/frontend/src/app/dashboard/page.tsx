"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import { fetchAnalyticsSummary, fetchRisks } from "@/lib/api";
import { analyticsKeys } from "@/lib/queryKeys";
import { FileText, Clock, AlertTriangle, DollarSign } from "lucide-react";

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

export default function DashboardPage() {
  const { user } = useAuth();

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

  const pendingReview =
    summary?.by_status?.["analyst_review"] ??
    0 + (summary?.by_status?.["pending_approval"] ?? 0);

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
