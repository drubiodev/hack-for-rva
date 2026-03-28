# Document Annotation Feature Plan

> **Date:** 2026-03-28
> **Status:** Planned
> **Owner:** Daniel (Frontend), Priyesh (Backend)

## Problem

Staff see OCR plain text on the left pane but can't interact with the actual document. No way to mark up specific sections, leave notes for colleagues, or visually connect AI-flagged risks to the source text. The review workflow is disconnected from the document itself.

## Goal

Replace the OCR text pane with a PDF/image viewer that supports click-to-annotate, enabling collaborative document markup during the review workflow.

## Annotation Schema (per document)

```ts
interface Annotation {
  id: string;            // "ann_" + timestamp
  x: number;             // % from left (0-100)
  y: number;             // % from top (0-100)
  page: number;          // 1-indexed
  text: string;          // the note content
  author: string;        // user.name
  initials: string;      // user.initials
  time: string;          // ISO 8601
}
```

Example:
```json
{
  "id": "ann_1774704335284",
  "x": "74.25",
  "y": "11.86",
  "page": 1,
  "text": "this is a test",
  "author": "Daniel",
  "initials": "D",
  "time": "2026-03-28T13:25:35.284Z"
}
```

## Architecture

| Concern | Approach |
|---|---|
| **PDF rendering** | `react-pdf` — renders pages as canvas, lightweight, no server component needed |
| **Image rendering** | Plain `<img>` with aspect-ratio container |
| **Annotation overlay** | Absolutely-positioned pins on `position: relative` wrapper per page, using `%` coordinates |
| **Storage** | JSONB column `annotations` on the `documents` table — no new tables, no migration complexity |
| **API** | 2 endpoints: `GET /api/v1/documents/{id}/annotations`, `POST /api/v1/documents/{id}/annotations` |
| **File serving** | `GET /api/v1/documents/{id}/file` — proxy from Azure Blob (already have `blob_url`) |
| **Optimistic UI** | Annotation appears instantly on click, syncs to backend in background |

## User Flow

1. **Open document detail page** — left pane loads the actual PDF/image (falls back to OCR text if no blob)
2. **Click anywhere on the document** — a pin drops at that position, text input opens
3. **Type a note, press Enter** — annotation saves, pin stays with author initials
4. **Hover a pin** — tooltip shows full note, author, timestamp
5. **Annotations from others** — visible as different-colored pins (based on initials hash)
6. **AI validation links** — clicking a validation alert scrolls to the relevant page (stretch goal)

## Implementation Tasks

### Backend

| # | Task | Files | Details |
|---|---|---|---|
| B1 | Add `annotations` JSONB column to `documents` table | `models/document.py`, Alembic migration | Default `[]`, stores array of annotation objects |
| B2 | Add annotation Pydantic schemas | `schemas/document.py` | `AnnotationCreate`, `AnnotationResponse` |
| B3 | `GET /api/v1/documents/{id}/annotations` | `api/router.py` | Returns `annotations` JSONB from document |
| B4 | `POST /api/v1/documents/{id}/annotations` | `api/router.py` | Appends to JSONB array, returns created annotation |
| B5 | `GET /api/v1/documents/{id}/file` | `api/router.py` | Proxy/redirect to Azure Blob URL for PDF/image serving |

### Frontend

| # | Task | Files | Details |
|---|---|---|---|
| F1 | Add `Annotation` type + API functions | `lib/types.ts`, `lib/api.ts` | Type definition, `fetchAnnotations()`, `createAnnotation()` |
| F2 | Install `react-pdf` + create `DocumentViewer` component | `components/DocumentViewer.tsx` | PDF page rendering + image fallback + OCR text fallback |
| F3 | Create `AnnotationLayer` overlay component | `components/AnnotationLayer.tsx` | Pins, click-to-create, hover tooltips, color by author |
| F4 | Replace OCR text pane in detail page | `documents/[id]/page.tsx` | Swap left pane to `DocumentViewer` + `AnnotationLayer` |

## File Ownership

- **Backend files** (Priyesh): `models/document.py`, `schemas/document.py`, `api/router.py`
- **Frontend files** (Daniel): `components/DocumentViewer.tsx`, `components/AnnotationLayer.tsx`, `documents/[id]/page.tsx`, `lib/types.ts`, `lib/api.ts`
- No shared file edits needed — backend/frontend coordinate via the API contract

## Demo Impact

- **Visual proof of review** — judges see staff actually marking up real City contracts, not just reading AI output
- **Collaboration narrative** — analyst pins a concern, supervisor sees it when approving
- **Bridges AI and human review** — AI flags a risk, human annotates the exact clause
- **Differentiation** — most hackathon teams show dashboards; this shows a working document workflow

## Scope Cuts (if time-pressed)

1. **Skip PDF rendering** — overlay annotations on the OCR text pane instead (much simpler, still valuable)
2. **Skip `/file` proxy** — use `blob_url` directly if CORS allows
3. **Skip multi-page navigation** — render page 1 only
4. **Skip author color differentiation** — all pins same color

## Guardrails

- Annotations are labeled as staff notes, not official records
- Annotation content is not fed back into AI extraction
- All annotations include author attribution (audit trail)
- Follows existing role model: analysts and supervisors can both annotate
