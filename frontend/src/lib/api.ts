import type {
  ServiceRequestList,
  ServiceRequestDetail,
  AnalyticsSummary,
  AnalyticsTrend,
} from "./types"

const BASE = process.env.NEXT_PUBLIC_API_URL

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`)
  return res.json() as Promise<T>
}

export const api = {
  getRequests: async (params?: {
    status?: string
    category?: string
    limit?: number
    offset?: number
  }) => {
    const url = new URL(`${BASE}/api/v1/requests`)
    if (params?.status) url.searchParams.set("status", params.status)
    if (params?.category) url.searchParams.set("category", params.category)
    if (params?.limit) url.searchParams.set("limit", String(params.limit))
    if (params?.offset) url.searchParams.set("offset", String(params.offset))
    return handleResponse<ServiceRequestList>(await fetch(url.toString()))
  },

  getRequest: async (id: number) =>
    handleResponse<ServiceRequestDetail>(
      await fetch(`${BASE}/api/v1/requests/${id}`)
    ),

  getAnalyticsSummary: async () =>
    handleResponse<AnalyticsSummary>(
      await fetch(`${BASE}/api/v1/analytics/summary`)
    ),

  getAnalyticsTrend: async (days?: number) => {
    const url = new URL(`${BASE}/api/v1/analytics/trend`)
    if (days) url.searchParams.set("days", String(days))
    return handleResponse<AnalyticsTrend>(await fetch(url.toString()))
  },
}
