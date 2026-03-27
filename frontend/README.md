# RVA 311 — Frontend Dashboard

Next.js 16 operations dashboard for viewing and managing 311 service requests.

## Structure

```
src/
├── app/
│   ├── layout.tsx                  # Root layout (QueryProvider, TooltipProvider)
│   ├── page.tsx                    # Redirect to /dashboard
│   └── dashboard/
│       ├── layout.tsx              # Sidebar navigation shell
│       ├── page.tsx                # Overview (KPI cards, category chart, recent requests)
│       ├── requests/
│       │   ├── page.tsx            # Request list (TanStack Table, filters, pagination)
│       │   └── [id]/page.tsx       # Request detail + conversation history
│       ├── map/page.tsx            # Leaflet map with request markers
│       └── analytics/page.tsx      # Charts (category pie, daily trend)
├── components/
│   ├── ui/                         # shadcn/ui (auto-generated, do not hand-edit)
│   ├── AppSidebar.tsx              # Navigation sidebar
│   ├── KpiCard.tsx                 # Summary metric card
│   ├── StatusBadge.tsx             # Status + category badges
│   └── LeafletMap.tsx              # Leaflet map (client-only)
├── lib/
│   ├── api.ts                      # All fetch calls (no inline fetches in components)
│   ├── types.ts                    # TypeScript types mirroring docs/openapi.yaml
│   └── queryKeys.ts                # TanStack Query key factory
└── providers/
    └── QueryProvider.tsx           # TanStack Query client provider
```

## Setup

```bash
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL
npm install
npm run dev
```

## Key design decisions

- **No WebSockets/SSE** — TanStack Query `refetchInterval: 30_000` for live updates
- **No direct Leaflet import** — `dynamic()` with `ssr: false` to avoid SSR crashes
- **`output: "standalone"`** in next.config.ts — required for Railway Docker builds
- **All fetch calls in `lib/api.ts`** — single place to update when backend URL changes
- **Types mirror OpenAPI** — `lib/types.ts` must match `docs/openapi.yaml` exactly
