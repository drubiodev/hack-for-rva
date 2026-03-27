"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts"
import { Inbox, BarChart3 } from "lucide-react"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"
import { KpiCard } from "@/components/KpiCard"
import { StatusBadge, CategoryBadge } from "@/components/StatusBadge"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import type { ChartConfig } from "@/components/ui/chart"

const categoryChartConfig: ChartConfig = {
  count: { label: "Requests", color: "var(--chart-1)" },
}

export default function DashboardOverview() {
  const router = useRouter()

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: queryKeys.analyticsSummary(),
    queryFn: api.getAnalyticsSummary,
    refetchInterval: 30_000,
  })

  const { data: requests, isLoading: requestsLoading } = useQuery({
    queryKey: queryKeys.requests(),
    queryFn: () => api.getRequests({ limit: 5 }),
    refetchInterval: 30_000,
  })

  const categoryData = summary
    ? Object.entries(summary.by_category).map(([name, count]) => ({
        name,
        count,
      }))
    : []

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {summaryLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))
        ) : (
          <>
            <KpiCard
              title="Total Requests"
              value={summary?.total_requests ?? 0}
            />
            <KpiCard
              title="New"
              value={summary?.by_status?.new ?? 0}
              description="Awaiting triage"
            />
            <KpiCard
              title="In Progress"
              value={summary?.by_status?.in_progress ?? 0}
              description="Being worked on"
            />
            <KpiCard
              title="Resolved"
              value={summary?.by_status?.resolved ?? 0}
              description="Completed"
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Requests by Category</CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-[300px]" />
            ) : categoryData.length === 0 ? (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 text-muted-foreground">
                <BarChart3 className="h-12 w-12 stroke-1" />
                <p className="text-sm font-medium">No category data yet</p>
              </div>
            ) : (
              <ChartContainer config={categoryChartConfig} className="h-[300px] w-full">
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" tickLine={false} axisLine={false} />
                  <YAxis tickLine={false} axisLine={false} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar
                    dataKey="count"
                    fill="var(--color-count)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Requests</CardTitle>
          </CardHeader>
          <CardContent>
            {requestsLoading ? (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-10" />
                ))}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ref #</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requests?.items.map((req) => (
                    <TableRow
                      key={req.id}
                      className="cursor-pointer"
                      onClick={() =>
                        router.push(`/dashboard/requests/${req.id}`)
                      }
                    >
                      <TableCell className="font-mono text-xs">
                        {req.reference_number}
                      </TableCell>
                      <TableCell>
                        <CategoryBadge category={req.category} />
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={req.status} />
                      </TableCell>
                    </TableRow>
                  ))}
                  {requests?.items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={3} className="py-8">
                        <div className="flex flex-col items-center gap-2 text-muted-foreground">
                          <Inbox className="h-8 w-8 stroke-1" />
                          <p className="text-sm font-medium">No requests yet</p>
                          <p className="text-xs">New SMS reports will appear here</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
