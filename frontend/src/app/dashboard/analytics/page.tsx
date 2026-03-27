"use client"

import { useQuery } from "@tanstack/react-query"
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts"
import { BarChart3 } from "lucide-react"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart"
import type { ChartConfig } from "@/components/ui/chart"

const PIE_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "oklch(0.65 0.15 230)",
  "oklch(0.55 0.12 150)",
  "oklch(0.75 0.1 50)",
]

export default function AnalyticsPage() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: queryKeys.analyticsSummary(),
    queryFn: api.getAnalyticsSummary,
    refetchInterval: 30_000,
  })

  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: queryKeys.analyticsTrend(30),
    queryFn: () => api.getAnalyticsTrend(30),
    refetchInterval: 30_000,
  })

  const categoryData = summary
    ? Object.entries(summary.by_category).map(([name, value], i) => ({
        name,
        value,
        fill: PIE_COLORS[i % PIE_COLORS.length],
      }))
    : []

  const categoryChartConfig: ChartConfig = Object.fromEntries(
    categoryData.map((d) => [
      d.name,
      { label: d.name.charAt(0).toUpperCase() + d.name.slice(1), color: d.fill },
    ])
  )

  const trendChartConfig: ChartConfig = {
    count: { label: "Requests", color: "var(--chart-1)" },
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Analytics</h2>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Category Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-[300px]" />
            ) : categoryData.length === 0 ? (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 text-muted-foreground">
                <BarChart3 className="h-12 w-12 stroke-1" />
                <p className="text-sm font-medium">No category data yet</p>
                <p className="text-xs">Analytics will appear as requests come in</p>
              </div>
            ) : (
              <ChartContainer config={categoryChartConfig} className="h-[300px] w-full">
                <PieChart>
                  <ChartTooltip content={<ChartTooltipContent nameKey="name" />} />
                  <Pie
                    data={categoryData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ name, percent }: { name?: string; percent?: number }) =>
                      `${name ?? ""} ${((percent ?? 0) * 100).toFixed(0)}%`
                    }
                  >
                    {categoryData.map((entry) => (
                      <Cell key={entry.name} fill={entry.fill} />
                    ))}
                  </Pie>
                  <ChartLegend content={<ChartLegendContent nameKey="name" />} />
                </PieChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Trend (30 days)</CardTitle>
          </CardHeader>
          <CardContent>
            {trendLoading ? (
              <Skeleton className="h-[300px]" />
            ) : (trend?.data ?? []).length === 0 ? (
              <div className="flex h-[300px] flex-col items-center justify-center gap-3 text-muted-foreground">
                <BarChart3 className="h-12 w-12 stroke-1" />
                <p className="text-sm font-medium">No trend data yet</p>
                <p className="text-xs">Daily request trends will appear here</p>
              </div>
            ) : (
              <ChartContainer config={trendChartConfig} className="h-[300px] w-full">
                <LineChart data={trend?.data ?? []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val: string) =>
                      new Date(val).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })
                    }
                  />
                  <YAxis tickLine={false} axisLine={false} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="var(--color-count)"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <Skeleton className="h-20" />
            ) : (
              <div className="flex gap-6">
                {Object.entries(summary?.by_status ?? {}).map(
                  ([status, count]) => (
                    <div key={status} className="text-center">
                      <p className="text-2xl font-bold tabular-nums">{count}</p>
                      <p className="text-sm capitalize text-muted-foreground">
                        {status.replace("_", " ")}
                      </p>
                    </div>
                  )
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
