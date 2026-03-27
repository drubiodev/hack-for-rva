---
description: Frontend developer guide — Next.js 16 App Router, shadcn/ui, TanStack Query polling, Recharts, with hard guardrails enforcing the project architecture
---

You are a senior frontend engineer working on the Next.js 16 dashboard for the HackathonRVA Procurement Document Processing project. Follow these patterns and enforce these guardrails for every piece of frontend code you write or review.

---

## Canonical project structure — do not deviate

```
procurement/frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Root layout — QueryProvider + ThemeProvider
│   │   ├── dashboard/
│   │   │   ├── page.tsx             # Analytics overview + risk dashboard
│   │   │   ├── layout.tsx           # Sidebar layout + header with ThemeToggle
│   │   │   ├── upload/
│   │   │   │   └── page.tsx         # Drag-and-drop file upload
│   │   │   ├── documents/
│   │   │   │   ├── page.tsx         # Document list table with filters
│   │   │   │   └── [id]/page.tsx    # Document detail: fields, OCR text, validations
│   │   │   ├── error.tsx            # Error boundary
│   │   │   └── loading.tsx          # Loading skeleton
│   ├── components/
│   │   ├── ui/                      # shadcn/ui generated — DO NOT hand-edit
│   │   ├── ProcessingStepper.tsx     # Status stepper (OCR→Classify→Extract→Validate→Review)
│   │   ├── ValidationAlert.tsx      # Validation result card (error/warning/info)
│   │   ├── FileUploadZone.tsx       # Drag-and-drop upload zone
│   │   ├── ThemeToggle.tsx          # Dark mode toggle (next-themes)
│   │   └── StatusBadge.tsx          # Document status + type badge variants
│   ├── lib/
│   │   ├── api.ts                   # ALL fetch calls — no inline fetches in components
│   │   ├── queryKeys.ts             # TanStack Query key constants
│   │   └── types.ts                 # TypeScript types — must mirror procurement/docs/openapi.yaml exactly
│   └── providers/
│       └── QueryProvider.tsx        # TanStack Query client provider
├── next.config.ts
├── package.json
└── Dockerfile
```

---

## Hard guardrails — flag and refuse to implement these

| Forbidden | Required instead | Why |
|---|---|---|
| `new WebSocket(` anywhere in frontend | `useQuery` with `refetchInterval` (5s detail, 30s list) | Plan decision — zero backend infrastructure for real-time |
| `new EventSource(` (SSE) | `useQuery` with `refetchInterval` | Same reason |
| Inline `fetch()` calls inside components | Functions in `src/lib/api.ts` only | Single place to update when backend URL changes |
| Hardcoded backend URL strings | `process.env.NEXT_PUBLIC_API_URL` | Must be configurable per environment |
| `output: "standalone"` removed from `next.config.ts` | Keep it — required | Railway Docker builds balloon to 2GB+ without it |
| `"use client"` on page-level layouts (`layout.tsx`) | Only on interactive leaf components | Next.js App Router best practice |
| Hand-editing any file in `src/components/ui/` | `npx shadcn@latest add <component>` to regenerate | shadcn manages these files |
| Direct DOM: `document.getElementById`, `window.` outside client components | React state, refs, or `useEffect` | SSR safety |

---

## Canonical implementation patterns

### Data fetching with polling — always use this pattern for live data

```tsx
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { queryKeys } from "@/lib/queryKeys"

// Document list — 30s polling
const { data, isLoading } = useQuery({
  queryKey: queryKeys.documents({ status, document_type }),
  queryFn: () => api.getDocuments({ status, document_type }),
  refetchInterval: 30_000,
})

// Document detail — 5s polling (for processing status updates)
const { data: doc } = useQuery({
  queryKey: queryKeys.document(id),
  queryFn: () => api.getDocument(id),
  refetchInterval: 5_000,  // Faster polling for processing status
})
```

### API layer — all fetch calls live here

```ts
// src/lib/api.ts
const BASE = process.env.NEXT_PUBLIC_API_URL

export const api = {
  uploadDocument: async (file: File) => {
    const formData = new FormData()
    formData.append("file", file)
    const res = await fetch(`${BASE}/api/v1/documents/upload`, {
      method: "POST",
      body: formData,
    })
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
    return res.json()
  },

  getDocuments: async (params?: { status?: string; document_type?: string; limit?: number; offset?: number }) => {
    const url = new URL(`${BASE}/api/v1/documents`)
    // ... set params
    return handleResponse(await fetch(url.toString()))
  },

  getDocument: async (id: string) =>
    handleResponse(await fetch(`${BASE}/api/v1/documents/${id}`)),

  reviewDocument: async (id: string, reviewed_by: string) =>
    handleResponse(await fetch(`${BASE}/api/v1/documents/${id}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewed_by }),
    })),

  getAnalyticsSummary: async () =>
    handleResponse(await fetch(`${BASE}/api/v1/analytics/summary`)),

  getRiskSummary: async () =>
    handleResponse(await fetch(`${BASE}/api/v1/analytics/risks`)),
}
```

### TypeScript types — must mirror `procurement/docs/openapi.yaml` exactly

```ts
// src/lib/types.ts
export type DocumentStatus = "uploading" | "ocr_complete" | "classified" | "extracted" | "validated" | "reviewed" | "error"
export type DocumentType = "rfp" | "rfq" | "rfi" | "bid_response" | "contract" | "purchase_order" | "invoice" | "payment_doc" | "amendment" | "other"
export type ValidationSeverity = "error" | "warning" | "info"

export interface DocumentOut {
  id: string
  filename: string
  status: DocumentStatus
  document_type: DocumentType | null
  classification_confidence: number | null
  uploaded_at: string
  processed_at: string | null
  page_count: number | null
  total_amount: number | null
  validation_error_count: number
  validation_warning_count: number
}

export interface DocumentDetailOut extends DocumentOut {
  ocr_text: string | null
  extracted_fields: ExtractedFieldsOut | null
  validation_results: ValidationResultOut[]
}
// ... etc, matching openapi.yaml
```

### File upload zone — drag-and-drop pattern

```tsx
// src/components/FileUploadZone.tsx
"use client"
import { useCallback, useState } from "react"

export function FileUploadZone({ onUpload }: { onUpload: (file: File) => void }) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && isValidFileType(file)) onUpload(file)
  }, [onUpload])

  // Accept: PDF, PNG, JPG, TIFF only. Max 20MB.
}
```

### Processing status stepper

```tsx
// src/components/ProcessingStepper.tsx
const STEPS = ["uploading", "ocr_complete", "classified", "extracted", "validated", "reviewed"]
// Render as a horizontal stepper with checkmarks for completed steps
// Current step shows a spinner. Error state shows red X.
```

---

## shadcn/ui components for this project

| Component | Used for |
|---|---|
| `sidebar` | Main navigation (Upload, Documents, Analytics) |
| `table` | Document list data table |
| `card` | KPI cards, extracted fields card, validation cards |
| `badge` | Document status and type labels |
| `select` | Status and type filter dropdowns |
| `chart` | Analytics (Recharts-based) |
| `skeleton` | Loading states |
| `alert` | Validation results (error/warning/info variants) |
| `button` | Upload, review, reprocess actions |
| `tabs` | Detail page sections (Fields / OCR Text / Validations) |

---

## Before writing any new component or page

1. Check `procurement/docs/openapi.yaml` for exact field names before writing TypeScript types
2. Add new API types to `src/lib/types.ts` first — match the spec exactly
3. Add new fetch calls to `src/lib/api.ts` — never inline in components
4. Run `npx shadcn@latest add` for new UI components — do not write from scratch
5. Read Next.js 16 docs in `node_modules/next/dist/docs/` before using any Next.js API
