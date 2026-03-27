"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"
import { Inbox } from "lucide-react"
import type { ServiceRequest } from "@/lib/types"
import { StatusBadge, CategoryBadge } from "@/components/StatusBadge"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const PAGE_SIZE = 20

const columnHelper = createColumnHelper<ServiceRequest>()

const columns = [
  columnHelper.accessor("reference_number", {
    header: "Reference #",
    cell: (info) => (
      <span className="font-mono text-xs">{info.getValue()}</span>
    ),
  }),
  columnHelper.accessor("category", {
    header: "Category",
    cell: (info) => <CategoryBadge category={info.getValue()} />,
  }),
  columnHelper.accessor("location", {
    header: "Location",
    cell: (info) => (
      <span className="max-w-[200px] truncate">
        {info.getValue() ?? "N/A"}
      </span>
    ),
  }),
  columnHelper.accessor("status", {
    header: "Status",
    cell: (info) => <StatusBadge status={info.getValue()} />,
  }),
  columnHelper.accessor("urgency", {
    header: "Urgency",
    cell: (info) => {
      const val = info.getValue()
      const color =
        val <= 2
          ? "text-green-600 dark:text-green-400"
          : val === 3
            ? "text-yellow-600 dark:text-yellow-400"
            : "text-red-600 dark:text-red-400"
      return <span className={`font-semibold ${color}`}>{val}</span>
    },
  }),
  columnHelper.accessor("created_at", {
    header: "Date",
    cell: (info) =>
      new Date(info.getValue()).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      }),
  }),
]

export default function RequestsPage() {
  const router = useRouter()
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [categoryFilter, setCategoryFilter] = useState<string>("")
  const [offset, setOffset] = useState(0)

  const { data, isLoading } = useQuery({
    queryKey: [
      ...queryKeys.requests({
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
      }),
      offset,
    ],
    queryFn: () =>
      api.getRequests({
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
        limit: PAGE_SIZE,
        offset,
      }),
    refetchInterval: 30_000,
  })

  const table = useReactTable({
    data: data?.items ?? [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <Select
          value={statusFilter}
          onValueChange={(val: string | null) => {
            setStatusFilter(!val || val === "all" ? "" : val)
            setOffset(0)
          }}
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="new">New</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={categoryFilter}
          onValueChange={(val: string | null) => {
            setCategoryFilter(!val || val === "all" ? "" : val)
            setOffset(0)
          }}
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            <SelectItem value="pothole">Pothole</SelectItem>
            <SelectItem value="streetlight">Streetlight</SelectItem>
            <SelectItem value="graffiti">Graffiti</SelectItem>
            <SelectItem value="trash">Trash</SelectItem>
            <SelectItem value="water">Water</SelectItem>
            <SelectItem value="sidewalk">Sidewalk</SelectItem>
            <SelectItem value="noise">Noise</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-12" />
          ))}
        </div>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border">
            <Table className="min-w-[600px]">
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHead key={header.id}>
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                      </TableHead>
                    ))}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length}
                      className="py-12"
                    >
                      <div className="flex flex-col items-center gap-3 text-muted-foreground">
                        <Inbox className="h-12 w-12 stroke-1" />
                        <p className="text-sm font-medium">No requests found</p>
                        <p className="text-xs">Try adjusting your filters or check back later</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  table.getRowModel().rows.map((row) => (
                    <TableRow
                      key={row.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() =>
                        router.push(
                          `/dashboard/requests/${row.original.id}`
                        )
                      }
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {data?.total ?? 0} total requests
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages || 1}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage >= totalPages}
                onClick={() => setOffset(offset + PAGE_SIZE)}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
