"use client"

import { Badge } from "@/components/ui/badge"
import type { ServiceRequestStatus, ServiceRequestCategory } from "@/lib/types"

const statusConfig: Record<
  ServiceRequestStatus,
  { label: string; className: string }
> = {
  new: {
    label: "New",
    className: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  },
  in_progress: {
    label: "In Progress",
    className:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  },
  resolved: {
    label: "Resolved",
    className:
      "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  },
}

export function StatusBadge({ status }: { status: ServiceRequestStatus }) {
  const config = statusConfig[status]
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  )
}

const categoryLabels: Record<ServiceRequestCategory, string> = {
  pothole: "Pothole",
  streetlight: "Streetlight",
  graffiti: "Graffiti",
  trash: "Trash",
  water: "Water",
  sidewalk: "Sidewalk",
  noise: "Noise",
  other: "Other",
}

export function CategoryBadge({
  category,
}: {
  category: ServiceRequestCategory
}) {
  return <Badge variant="secondary">{categoryLabels[category]}</Badge>
}
