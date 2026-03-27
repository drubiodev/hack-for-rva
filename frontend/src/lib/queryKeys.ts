export const queryKeys = {
  requests: (filters?: { status?: string; category?: string }) =>
    ["requests", filters ?? {}] as const,
  request: (id: number) => ["requests", id] as const,
  analyticsSummary: () => ["analytics", "summary"] as const,
  analyticsTrend: (days?: number) => ["analytics", "trend", days ?? 7] as const,
}
