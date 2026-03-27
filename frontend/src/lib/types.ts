export type ServiceRequestStatus = "new" | "in_progress" | "resolved"
export type ServiceRequestCategory =
  | "pothole"
  | "streetlight"
  | "graffiti"
  | "trash"
  | "water"
  | "sidewalk"
  | "noise"
  | "other"

export interface ServiceRequest {
  id: number
  reference_number: string
  category: ServiceRequestCategory
  description: string
  location: string | null
  latitude: number | null
  longitude: number | null
  urgency: number
  status: ServiceRequestStatus
  phone: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  direction: "inbound" | "outbound"
  body: string
  created_at: string
}

export interface ServiceRequestDetail extends ServiceRequest {
  messages: Message[]
}

export interface ServiceRequestList {
  items: ServiceRequest[]
  total: number
  limit: number
  offset: number
}

export interface AnalyticsSummary {
  total_requests: number
  by_status: Record<string, number>
  by_category: Record<string, number>
}

export interface TrendPoint {
  date: string
  count: number
}

export interface AnalyticsTrend {
  days: number
  data: TrendPoint[]
}
