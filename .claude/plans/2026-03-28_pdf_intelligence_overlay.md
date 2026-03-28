# ContractIQ — PDF Intelligence Overlay

> Architecture and product plan for highlighting source passages in documents, linking extracted intelligence back to the exact text that produced it.

---

## Product Vision

The most powerful moment in a procurement review is when staff can **see exactly which sentence** in a 50-page contract triggered a risk flag, where the expiration date was found, or why an MBE/WBE requirement was flagged. Today, the detail page shows extracted fields on the left and raw OCR text on the right — but there's no connection between them. The user must mentally search for "where did the AI find $2,000,000 for general liability?"

**The goal:** When a user clicks on an extracted field (e.g., "Expiration Date: Dec 14, 2021"), the document viewer scrolls to and highlights the exact passage in the contract where that date was found. When viewing the document, risk passages glow red, compliance clauses glow green, and financial terms glow blue — all automatically.

---

## The Data We Have (and What We're Throwing Away)

### Azure Document Intelligence Response

The `prebuilt-read` model returns rich positional data that we currently **discard** — we only keep `result.content` (text) and word-level confidence scores:

```python
result.pages[i].words[j] = {
    "content": "expiration",      # the word
    "confidence": 0.99,           # recognition confidence
    "polygon": [x1,y1, x2,y2, x3,y3, x4,y4],  # 4-corner bounding box
    "span": {"offset": 1234, "length": 10}       # character offset in full text
}

result.pages[i] = {
    "page_number": 1,
    "width": 8.5,                 # page dimensions
    "height": 11.0,
    "unit": "inch",               # or "pixel" for images
    "words": [...],
    "lines": [...],               # grouped into lines with polygons
    "spans": [{"offset": 0, "length": 5000}]  # character range for this page
}
```

**Key insight:** The `span.offset` maps every word to its position in the concatenated `result.content` string. If we store this mapping, we can go from "the AI found expiration date at characters 1234-1244 in the OCR text" → "that text is at polygon [x1,y1,...] on page 3."

### What the Extractor Already Returns

The LLM extraction already returns `expiration_date_source` — an exact quote from the document. We could extend this pattern to ALL fields:

```json
{
  "expiration_date": "2021-12-14",
  "expiration_date_source": "Contract expires December 14, 2021 per Section 2.1",
  "vendor_name": "AXON ENTERPRISE INC",
  "total_amount": 3399896.25
}
```

If we also ask the LLM to return the source quote for each field, we can text-search the OCR text for those quotes and highlight them.

---

## Architecture: Three Layers

### Layer 1: OCR Span Storage (Backend — capture the data)

Store the DI word-level span data so we can map character offsets to page positions later.

**What to store:** Not every word polygon (too large for 50-page docs), but a **page-level span index** — which character offset range belongs to which page:

```python
# Compact representation: ~100 bytes per page vs. ~50KB for all word polygons
ocr_pages = [
    {"page": 1, "offset": 0, "length": 4800, "width": 8.5, "height": 11.0, "unit": "inch"},
    {"page": 2, "offset": 4800, "length": 5200, "width": 8.5, "height": 11.0, "unit": "inch"},
    ...
]
```

For a richer overlay (word-level highlighting on actual PDF pages), also store **line-level spans** — still much smaller than word-level:

```python
ocr_lines = [
    {"page": 1, "offset": 0, "length": 85, "polygon": [0.5, 1.2, 7.8, 1.2, 7.8, 1.4, 0.5, 1.4]},
    {"page": 1, "offset": 85, "length": 92, "polygon": [0.5, 1.5, 7.8, 1.5, 7.8, 1.7, 0.5, 1.7]},
    ...
]
```

**Storage:** New JSONB column `ocr_metadata` on `Document` model (already has `ocr_text` as TEXT).

### Layer 2: Source Attribution (Extractor — map fields to text spans)

Extend the LLM extraction prompt to return **source quotes** for every field, not just `expiration_date_source`:

```json
{
  "field_sources": {
    "expiration_date": "Contract expires December 14, 2021",
    "total_amount": "not to exceed Three Million Three Hundred Ninety-Nine Thousand",
    "vendor_name": "AXON ENTERPRISE INC",
    "insurance_general_liability_min": "Commercial General Liability: combined limit not less than $2,000,000",
    "mbe_wbe_required": "MBE/WBE participation and affidavit requirements per City policy",
    "liquidated_damages_rate": "liquidated damages at the rate of $600.00 per calendar day",
    "renewal_clause": "automatically renew for successive one (1) year periods"
  }
}
```

Then **text-search** the OCR text for each source quote to find the character offset:

```python
def find_source_spans(ocr_text: str, field_sources: dict) -> list[dict]:
    """Find character offsets for each field's source quote in the OCR text."""
    highlights = []
    for field, quote in field_sources.items():
        idx = ocr_text.lower().find(quote.lower())
        if idx >= 0:
            highlights.append({
                "field": field,
                "offset": idx,
                "length": len(quote),
                "category": categorize_field(field),  # "risk", "compliance", "financial", "date", "identity"
            })
    return highlights
```

**Category coloring:**
| Category | Fields | Color |
|---|---|---|
| `risk` | expiration_date, renewal_clause, liquidated_damages_rate | Red (#DC2626) |
| `compliance` | mbe_wbe_required, mbe_wbe_details, federal_funding, compliance_flags | Green (#059669) |
| `financial` | total_amount, insurance minimums, bond amounts | Blue (#2563EB) |
| `identity` | vendor_name, issuing_department, document_number | Purple (#7C3AED) |
| `date` | effective_date, document_date | Amber (#D97706) |

### Layer 3: Frontend Rendering (two modes)

#### Mode A: OCR Text Highlights (works for ALL documents)

For documents where we only have OCR text (no PDF):

1. Split `ocr_text` into segments at highlight boundaries
2. Wrap highlighted segments in `<mark>` elements with category colors
3. On left-pane field click → scroll right pane to the highlighted segment
4. On right-pane highlight click → expand the corresponding field on the left

```tsx
function HighlightedText({ text, highlights, onHighlightClick }) {
  // Sort highlights by offset, merge overlapping
  // Build array of {text, highlight?} segments
  // Render: plain <span> for non-highlighted, <mark> for highlighted
}
```

This is the **primary rendering mode** since most documents only have OCR text.

#### Mode B: PDF Page Overlay (works for uploaded PDFs with blob_url)

For documents where we have the original PDF AND line-level polygon data:

1. Render actual PDF pages via `<iframe>` or `pdf.js` canvas
2. Overlay transparent colored rectangles at the polygon coordinates
3. Scale polygons from DI units (inches) to rendered pixel coordinates

This is a **nice-to-have** for v1 — Mode A covers 100% of documents, Mode B adds visual fidelity for uploaded PDFs.

---

## Data Flow

```
                    Upload PDF
                        ↓
              Azure Document Intelligence
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    ocr_text     ocr_metadata       confidence
    (full text)  (page spans,        (per-word)
                  line polygons)
        ↓
    GPT-4 mini Extraction
        ↓
    ┌───────┼───────────┐
    ↓       ↓           ↓
  fields  field_sources  confidences
    ↓       ↓
    └───┬───┘
        ↓
    find_source_spans(ocr_text, field_sources)
        ↓
    highlights = [{field, offset, length, category}]
        ↓
    Store in extracted_fields.source_highlights (JSONB)
        ↓
    Frontend renders <mark> tags on OCR text
```

---

## Implementation Stories

### S32: Capture OCR Page & Line Metadata from Azure DI

**As a** system processing uploaded PDFs,
**I want** to store the page dimensions and line-level span data from Azure DI,
**so that** I can map extracted fields back to their source location in the document.

**Implementation:**
- Add `ocr_metadata` JSONB column to `Document` model
- In `azure_di.py`, after OCR completes, extract and store:
  ```python
  metadata = {
      "pages": [
          {
              "page": page.page_number,
              "width": page.width,
              "height": page.height,
              "unit": page.unit,
              "offset": page.spans[0].offset if page.spans else 0,
              "length": page.spans[0].length if page.spans else 0,
          }
          for page in result.pages
      ],
      "lines": [
          {
              "page": page.page_number,
              "content": line.content,
              "offset": line.spans[0].offset if line.spans else 0,
              "length": line.spans[0].length if line.spans else 0,
              "polygon": line.polygon,  # [x1,y1,...,x4,y4]
          }
          for page in result.pages
          for line in (page.lines or [])
      ] if settings.store_ocr_lines else [],  # Optional: skip for budget
  }
  ```
- Update `extract_text()` return signature to include metadata: `tuple[str, float, dict]`
- Store metadata in `doc.ocr_metadata` in pipeline.py

**Files:** `azure_di.py`, `service.py`, `pipeline.py`, `models/document.py`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] `Document.ocr_metadata` contains page-level span index after OCR
- [ ] Metadata correctly maps character offsets to page numbers
- [ ] Non-Azure paths (text layer, pre-OCR) store empty metadata `{}`
- [ ] Backend tests pass

---

### S33: Extend Extraction to Return Source Quotes per Field

**As a** system extracting structured data from contracts,
**I want** the LLM to return the exact source quote for each extracted field,
**so that** I can highlight the source passage in the document viewer.

**Implementation:**
- Add `field_sources` to the extraction JSON schema:
  ```python
  "field_sources": {
      "type": "object",
      "description": "For each extracted field, provide the EXACT quote (10-100 chars) from the document text where you found the value. Only include fields you actually extracted.",
      "properties": {
          "vendor_name": {"type": ["string", "null"]},
          "total_amount": {"type": ["string", "null"]},
          "effective_date": {"type": ["string", "null"]},
          "expiration_date": {"type": ["string", "null"]},
          "insurance_general_liability_min": {"type": ["string", "null"]},
          "mbe_wbe_required": {"type": ["string", "null"]},
          "renewal_clause": {"type": ["string", "null"]},
          "liquidated_damages_rate": {"type": ["string", "null"]},
          "bond_required": {"type": ["string", "null"]},
          "procurement_method": {"type": ["string", "null"]},
      },
      "required": [...],
      "additionalProperties": false,
  }
  ```
- Add `_compute_source_highlights()` function in pipeline.py:
  - Takes `ocr_text` and `field_sources` dict
  - For each source quote, finds its character offset in the OCR text (case-insensitive fuzzy match)
  - Returns array of `{field, offset, length, category, quote}` objects
- Store result in `extracted_fields.source_highlights` (new JSONB column)
- Increase `max_completion_tokens` to account for the additional output

**Files:** `extractor.py`, `pipeline.py`, `models/document.py`, `schemas/document.py`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] LLM returns `field_sources` with exact quotes for extracted fields
- [ ] `source_highlights` contains character offset mappings for found quotes
- [ ] Unfound quotes (fuzzy match fail) are skipped, not stored
- [ ] Works for both short (1-page) and long (50-page, smart-truncated) documents
- [ ] Backend tests pass

---

### S34: Highlighted OCR Text Viewer (Frontend)

**As an** analyst reviewing a contract in the detail page,
**I want** extracted field source passages highlighted in color on the document text,
**so that** I can verify exactly where the AI found each data point.

**Implementation:**
- Add `HighlightedText` component:
  ```tsx
  interface SourceHighlight {
    field: string;
    offset: number;
    length: number;
    category: "risk" | "compliance" | "financial" | "identity" | "date";
    quote: string;
  }

  function HighlightedText({ text, highlights, activeField, onHighlightClick })
  ```
  - Splits text at highlight boundaries into segments
  - Renders highlights as `<mark>` elements with category background colors
  - Active highlight (from left-pane click) gets a pulsing border animation
  - Clicking a highlight triggers `onHighlightClick(field)` which scrolls left pane to that field

- Replace the plain `<pre>{doc.ocr_text}</pre>` in the right pane with:
  ```tsx
  <HighlightedText
    text={doc.ocr_text}
    highlights={fields?.source_highlights ?? []}
    activeField={activeHighlightField}
    onHighlightClick={(field) => scrollToField(field)}
  />
  ```

- Add bidirectional linking:
  - Left pane: clicking a field name sets `activeHighlightField` state → right pane scrolls to and pulses the highlight
  - Right pane: clicking a highlight → left pane scrolls to and pulses the corresponding extracted field

- Category color legend in the toolbar:
  ```
  [Risk] [Compliance] [Financial] [Identity] [Date]  — small colored dots with labels
  ```

**Files:** New `components/HighlightedText.tsx`, `documents/[id]/page.tsx`, `lib/types.ts`

**Effort:** 2 hours

**Acceptance Criteria:**
- [ ] Extracted fields with source quotes are highlighted in the OCR text
- [ ] Highlights are color-coded by category (risk=red, compliance=green, financial=blue, identity=purple, date=amber)
- [ ] Clicking a field on the left scrolls the right pane to its source highlight
- [ ] Clicking a highlight on the right identifies the corresponding field
- [ ] Active highlight has a pulsing/glowing border animation
- [ ] Documents without highlights (Socrata, error state) render normally
- [ ] Zoom level applies correctly to highlighted text
- [ ] `npx tsc --noEmit` passes

---

### S35: Interactive Annotation Pins on Highlighted Text

**As an** analyst reviewing highlighted passages,
**I want to** click on any text passage (highlighted or not) and leave an annotation,
**so that** I can flag concerns for supervisor review.

This integrates the existing `AnnotationLayer` with the new highlighted text viewer.

**Implementation:**
- Restyle `AnnotationLayer` for the light theme (S29 from annotation plan)
- Render the annotation layer as an overlay on the highlighted text container
- Annotations and highlights coexist — pins sit on top of colored highlights
- The toolbar shows both annotation count AND highlight legend

**Files:** `components/AnnotationLayer.tsx`, `documents/[id]/page.tsx`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Annotations can be placed on highlighted passages
- [ ] Annotation pins are visible on top of colored highlights
- [ ] Hover tooltip shows annotation text
- [ ] Both highlights and annotations scroll together
- [ ] `npx tsc --noEmit` passes

---

### S36: PDF Page Rendering with Polygon Overlays (Nice-to-Have)

**As a** analyst reviewing an uploaded PDF with OCR,
**I want** to see the actual PDF page with colored overlays on the source passages,
**so that** I can verify the AI's extraction against the original document layout.

**Implementation:**
- Use `react-pdf` (pdf.js wrapper) to render actual PDF pages from `blob_url`
- Overlay colored rectangles using the line-level polygon data from `ocr_metadata`
- Map polygon coordinates from DI units (inches/pixels) to rendered page pixels
- Scale with zoom level

This requires:
- `npm install react-pdf`
- A `/api/v1/documents/{id}/file` proxy endpoint to serve the blob (already exists per test_annotations.py)
- Canvas-based polygon rendering

**Effort:** 4 hours (significant complexity with coordinate transforms and pdf.js)

**This is a v2 feature** — Mode A (highlighted OCR text) covers 100% of documents and ships faster.

---

## Implementation Priority

```
S33 Source quotes in extraction   ██████████████ 1.5h  ← Unlocks everything
S34 Highlighted text viewer       ████████████████ 2h  ← Core UX feature
S32 OCR metadata capture          ████████████ 1h      ← Needed for page mapping
S35 Annotation integration        ████████ 45m         ← Combines both features
──────────────────────────────────────────────────────
Total MUST-HAVE:                  ~5.25 hours

S36 PDF page rendering            ████████████████████ 4h ← v2 nice-to-have
```

---

## Example: What the User Sees

### Left Pane — Extracted Fields (clickable)
```
EXPIRATION DATE          ← click this
Dec 14, 2021  [90% conf] [source: "Contract expires December 14, 2021"]
```

### Right Pane — Document Text (highlighted)
```
... Section 2.1 Term and Termination.

The initial term of this Agreement shall commence on the
Effective Date and shall continue for a period of five (5) years.

┌─────────────────────────────────────────────────┐
│ Contract expires December 14, 2021 per the terms│  ← RED highlight (risk)
│ set forth in Section 2.1 above.                 │     pulsing border when
└─────────────────────────────────────────────────┘     clicked from left pane

... Section 4.3 Insurance Requirements.

┌─────────────────────────────────────────────────┐
│ Commercial General Liability: combined limit    │  ← BLUE highlight (financial)
│ not less than $2,000,000 per occurrence         │
└─────────────────────────────────────────────────┘

... Section 7.2 MBE/WBE Participation.

┌─────────────────────────────────────────────────┐
│ Contractor shall maintain MBE/WBE participation │  ← GREEN highlight (compliance)
│ in accordance with City policy Section 21-46    │
└─────────────────────────────────────────────────┘
```

### Toolbar
```
[filename.pdf] [OCR 95%]  ⬤Risk ⬤Compliance ⬤Financial  [zoom] [2 notes] [print]
```

---

## Why This Approach Over PDF.js

| Factor | OCR Text Highlights (Mode A) | PDF.js + Polygons (Mode B) |
|---|---|---|
| **Works for** | All 1,375 documents | Only uploaded PDFs with blob_url (~10) |
| **Complexity** | Low — string splitting + `<mark>` tags | High — pdf.js, canvas, coordinate transforms |
| **Performance** | Fast — DOM-based text rendering | Heavy — canvas rendering per page |
| **Zoom** | CSS font-size — trivial | Canvas re-render at each zoom level |
| **Text selection** | Works natively | Requires custom text layer |
| **Annotations** | Click on DOM elements | Canvas click → coordinate mapping |
| **Time to build** | ~4 hours | ~8 hours |
| **Demo impact** | High — "AI shows its work" | Higher — actual PDF with overlays |

**Recommendation:** Ship Mode A for the hackathon. It covers 100% of documents, demonstrates the "AI shows its work" story, and builds the data pipeline (source quotes, highlight mapping) that Mode B needs anyway.
