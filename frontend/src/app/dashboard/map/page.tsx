"use client"

import dynamic from "next/dynamic"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"

const LeafletMap = dynamic(() => import("@/components/LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[600px] animate-pulse rounded-xl bg-muted" />
  ),
})

export default function MapPage() {
  const { data } = useQuery({
    queryKey: queryKeys.requests(),
    queryFn: () => api.getRequests({ limit: 100 }),
    refetchInterval: 30_000,
  })

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Request Map</h2>
      <div className="h-[600px] rounded-xl border">
        <LeafletMap requests={data?.items ?? []} />
      </div>
    </div>
  )
}
