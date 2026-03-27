"use client"

import dynamic from "next/dynamic"
import { useQuery } from "@tanstack/react-query"
import { MapPin } from "lucide-react"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"

const LeafletMap = dynamic(() => import("@/components/LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[calc(100vh-12rem)] animate-pulse rounded-xl bg-muted" />
  ),
})

export default function MapPage() {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.requests(),
    queryFn: () => api.getRequests({ limit: 100 }),
    refetchInterval: 30_000,
  })

  const hasRequests = (data?.items ?? []).length > 0

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Request Map</h2>
      <div className="h-[calc(100vh-12rem)] rounded-xl border">
        {!isLoading && !hasRequests ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
            <MapPin className="h-12 w-12 stroke-1" />
            <p className="text-sm font-medium">No requests to display on the map</p>
            <p className="text-xs">Requests with location data will appear here</p>
          </div>
        ) : (
          <LeafletMap requests={data?.items ?? []} />
        )}
      </div>
    </div>
  )
}
