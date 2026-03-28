# ContractIQ — Document Annotation System

> Architecture and product plan for collaborative document annotations overlaid on the OCR text viewer.

---

## Product Vision

City procurement analysts review contracts and need to **mark up specific passages** — flagging ambiguous clauses, noting risks, asking questions for supervisor review. Today they print PDFs and use sticky notes. ContractIQ should bring this workflow into the digital tool, directly on the document text.

### User Stories

**As an** analyst reviewing a contract in the split-view detail page,
**I want to** click on a passage in the document text and leave a note,
**so that** my supervisor can see exactly what I flagged when they review.

**As a** supervisor approving a contract,
**I want to** see all analyst annotations pinned to the exact text location,
**so that** I can verify they reviewed the critical clauses before I approve.

**As a** team reviewing a contract over multiple sessions,
**I want to** see who left each annotation and when,
**so that** I can follow the review conversation chronologically.

---

## Current State

### What Exists (built but not wired together)

| Layer | Status | What's There |
|---|---|---|
| **Database** | Done | `annotations` JSONB column on `documents` table — stores array of `{id, x, y, page, text, author, initials, time}` |
| **API** | Done | `GET /api/v1/documents/{id}/annotations` + `POST .../annotations` — with validation, activity logging, auto-generated ID/timestamp |
| **Tests** | Done | 7 tests in `test_annotations.py` — CRUD, 404 handling, activity logging |
| **Frontend Types** | Done | `Annotation` and `AnnotationCreate` interfaces in `types.ts` |
| **API Client** | Done | `fetchAnnotations()` and `createAnnotation()` in `api.ts` |
| **Component** | Done | `AnnotationLayer.tsx` — click-to-create pins, hover tooltips, author color coding |
| **Page Integration** | **Not Done** | The detail page does not import or render `AnnotationLayer` |

### The Gap

The `AnnotationLayer` component exists and works, but it was designed for a **dark-mode, absolute-positioned overlay on a full-page view**. The current detail page uses a **light-mode split-view with a simulated PDF page inside a scrollable container**. The integration needs:

1. Wire `AnnotationLayer` into the right pane's document content area
2. Adapt the styling from dark-mode to the light "Modern Analyst" theme
3. Add TanStack Query hooks for fetching/creating annotations
4. Handle the coordinate system correctly (annotations positioned relative to the scrollable OCR text container, not the viewport)

---

## Architecture

### Data Model (no changes needed)

The existing schema is sound:

```
Document.annotations: JSONB = [
  {
    "id": "ann_a1b2c3d4e5f6",     // auto-generated
    "x": 45.2,                     // % of container width
    "y": 12.8,                     // % of container scrollHeight
    "page": 1,                     // page number (1-based)
    "text": "Verify this clause",  // annotation text
    "author": "Priyesh Jain",      // who wrote it
    "initials": "PJ",              // for color-coded pin
    "time": "2026-03-28T14:30:00Z" // auto-generated
  }
]
```

**Why x/y percentages?** The OCR text is rendered in a `<pre>` block that reflows with zoom. Percentage-based coordinates are zoom-invariant — an annotation at `y: 25%` stays at the 25% mark whether zoom is 80% or 150%.

**Why JSONB on the document row (not a separate table)?**
- Annotations are always loaded with the document (no lazy-loading scenario)
- Typically <50 annotations per document — no performance concern
- Simpler schema for a hackathon
- No need for cross-document annotation queries

### API (no changes needed)

```
GET  /api/v1/documents/{id}/annotations  → Annotation[]
POST /api/v1/documents/{id}/annotations  → Annotation (201)
     Body: { x, y, page, text, author, initials }
```

Activity log entry created on each annotation: `action: "annotation_added"`.

### Frontend Integration (the work to be done)

#### Coordinate System

The right pane structure is:

```
<div className="w-1/2 flex flex-col">          ← right pane
  <div className="h-10 bg-[#1F2937]">          ← toolbar (fixed)
  <div className="flex-1 overflow-auto p-6">    ← scroll container
    <div className="mx-auto bg-white shadow">   ← "paper" page
      <pre>{doc.ocr_text}</pre>                 ← text content
    </div>
  </div>
</div>
```

The `AnnotationLayer` must be positioned **inside the scroll container** (not inside the paper page) so that:
- Pins scroll with the text
- Click coordinates map to `scrollHeight` percentages
- Pins stay positioned correctly at any zoom level

```
<div className="flex-1 overflow-auto p-6 relative">   ← add relative
  <AnnotationLayer ... />                              ← overlay
  <div className="mx-auto bg-white shadow">
    <pre>{doc.ocr_text}</pre>
  </div>
</div>
```

#### Query Integration

```tsx
// Fetch annotations
const { data: annotations = [] } = useQuery({
  queryKey: ["annotations", id],
  queryFn: () => fetchAnnotations(id),
  enabled: !!doc?.ocr_text,  // only fetch if document has text
});

// Create mutation
const createAnnotationMutation = useMutation({
  mutationFn: (data: { x: number; y: number; text: string }) =>
    createAnnotation(id, {
      ...data,
      page: 1,  // OCR text is single-page for now
      author: user?.name ?? "Unknown",
      initials: user?.initials ?? "??",
    }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["annotations", id] });
  },
});
```

---

## Implementation Stories

### S28: Wire AnnotationLayer into Document Detail Page

**Implementation:**
1. Import `AnnotationLayer`, `fetchAnnotations`, `createAnnotation` in the detail page
2. Add `useQuery` for fetching annotations (enabled only when `doc.ocr_text` exists)
3. Add `useMutation` for creating annotations with optimistic update
4. Wrap the scroll container in `relative` positioning
5. Render `<AnnotationLayer>` inside the scroll container, above the paper div
6. Pass `disabled={!doc.ocr_text}` to prevent annotation on empty documents
7. Pass `annotations` data and `onAnnotationCreate` callback

**Files:** `procurement/frontend/src/app/dashboard/documents/[id]/page.tsx`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] Clicking on OCR text creates a pin at the click location
- [ ] Typing a note and pressing Enter saves the annotation
- [ ] Saved annotations appear as colored pins with initials
- [ ] Hovering a pin shows author, timestamp, and note text
- [ ] Annotations persist across page reloads (stored in DB)
- [ ] Annotations scroll with the document text
- [ ] Annotations reposition correctly when zoom changes
- [ ] Documents without OCR text show no annotation layer
- [ ] `npx tsc --noEmit` passes

---

### S29: Restyle AnnotationLayer for Light Theme

**Problem:** The existing `AnnotationLayer` uses dark-mode colors (`bg-[#1a1d27]`, `text-[#94a3b8]`, `border-[#2e3248]`). The detail page is now light-themed.

**Implementation:**
- Update tooltip background: `bg-white border-[#E7E5E4] shadow-lg`
- Update tooltip text: `text-[#292524]` for body, `text-[#78716C]` for meta
- Update input background: `bg-[#F7F5F2] border-[#E7E5E4]`
- Update input text: `text-[#292524] placeholder-[#A8A29E]`
- Keep pin colors as-is (they work on both light/dark backgrounds)
- Add subtle drop-shadow to pins for visibility on white paper

**Files:** `procurement/frontend/src/components/AnnotationLayer.tsx`

**Effort:** 15 minutes

**Acceptance Criteria:**
- [ ] Tooltips are readable on the light background
- [ ] Input box matches the "Modern Analyst" design tokens
- [ ] Pins are visible on white paper background
- [ ] Color-coded pins still distinguish different authors

---

### S30: Annotation Count Badge in Toolbar

**Implementation:**
- Show annotation count in the document viewer toolbar: "3 notes" badge
- Add a toggle button to show/hide annotation pins (for clean reading vs. review mode)
- When hidden, pins disappear but annotations are still in the DB

**Files:** `procurement/frontend/src/app/dashboard/documents/[id]/page.tsx`

**Effort:** 15 minutes

**Acceptance Criteria:**
- [ ] Toolbar shows "N notes" count next to the zoom controls
- [ ] Toggle button switches between showing/hiding pins
- [ ] Default state: pins visible

---

### S31: AI-Generated Annotation Suggestions (Nice-to-Have)

**As a** analyst reviewing a long contract,
**I want** the AI to pre-highlight risky or notable clauses,
**so that** I know where to focus my review.

**Implementation:**
- After extraction, run a secondary LLM pass that identifies "annotation-worthy" passages
- For each passage, generate a suggested annotation: `{text: "Auto-renewal clause — verify notice period", y: <position>}`
- Store as annotations with `author: "ContractIQ AI"`, `initials: "AI"`
- Display AI annotations with a distinct pin style (e.g., sparkle icon instead of initials)
- Analyst can dismiss or confirm AI suggestions

**This is a v2 feature** — requires calculating text position mapping (OCR character offset → y-percentage), which is non-trivial.

---

## Implementation Priority

```
S29 Restyle for light theme   ███ 15m    ← Must-do before integration
S28 Wire into detail page     ██████ 30m ← Core feature
S30 Toolbar badge + toggle    ███ 15m    ← Polish
─────────────────────────────────────────
Total MUST-HAVE:              ~1 hour

S31 AI annotation suggestions ████████████ 2h ← v2 nice-to-have
```

---

## Design Reference

From the Stitch PRD contract detail view, the right pane shows a PDF viewer with a dark toolbar and white paper content area. Annotations should appear as:

- **Pins:** Small colored circles (24x24px) with 2-letter initials, positioned at the annotation's x/y percentage
- **Tooltip on hover:** White card with author name, timestamp, and note text — appears to the right of the pin
- **Input on click:** Small input box with "Add a note..." placeholder, Enter to save, Escape to cancel
- **Visual hierarchy:** Pins sit above the text but don't obscure it (semi-transparent background, offset to the margin area when possible)

The toolbar in the Stitch design has space for annotation controls between the zoom and print buttons:

```
[filename] [OCR %]           [zoom-] [100%] [zoom+] | [3 notes] [toggle] | [print] [download]
```
