"use client"

import { use } from "react"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"
import { StatusBadge, CategoryBadge } from "@/components/StatusBadge"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/card"

export default function RequestDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const requestId = parseInt(id, 10)

  const { data: request, isLoading } = useQuery({
    queryKey: queryKeys.request(requestId),
    queryFn: () => api.getRequest(requestId),
    refetchInterval: 30_000,
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-48" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!request) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Request not found</p>
        <Link href="/dashboard/requests">
          <Button variant="outline" className="mt-4">Back to requests</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/dashboard/requests">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="size-4 mr-1" />
            Back
          </Button>
        </Link>
        <h2 className="text-lg font-semibold">{request.reference_number}</h2>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground w-20">Status</span>
              <StatusBadge status={request.status} />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground w-20">Category</span>
              <CategoryBadge category={request.category} />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground w-20">Urgency</span>
              <span className="font-semibold">{request.urgency}/5</span>
            </div>
            <div>
              <span className="text-sm text-muted-foreground">Description</span>
              <p className="mt-1 text-sm">{request.description}</p>
            </div>
            {request.location && (
              <div>
                <span className="text-sm text-muted-foreground">Location</span>
                <p className="mt-1 text-sm">{request.location}</p>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground w-20">Phone</span>
              <span className="font-mono text-sm">{request.phone}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground w-20">Created</span>
              <span className="text-sm">
                {new Date(request.created_at).toLocaleString()}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Conversation</CardTitle>
            <CardDescription>SMS message history</CardDescription>
          </CardHeader>
          <CardContent>
            {request.messages.length === 0 ? (
              <p className="text-sm text-muted-foreground">No messages yet</p>
            ) : (
              <div className="space-y-3">
                {request.messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${
                      msg.direction === "outbound"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                        msg.direction === "outbound"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <p>{msg.body}</p>
                      <p
                        className={`mt-1 text-xs ${
                          msg.direction === "outbound"
                            ? "text-primary-foreground/70"
                            : "text-muted-foreground"
                        }`}
                      >
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
