# Chatbot & Semantic Search UX — Design + Product Plan

> **Status:** Ready for implementation
> **Date:** 2026-03-28
> **Roles:** Product Manager + UX Designer + Architect
> **Depends on:** Semantic search backend (completed), existing chat components

---

## 1. Current State & Problems

The chat infrastructure exists but is **disconnected from the experience**:

- `ChatPanel.tsx` (slide-out panel) is built but **never mounted** — `ChatPanelProvider` is not in the layout
- `/dashboard/chat` (full page) exists but is **not in the sidebar nav**
- No chat trigger button anywhere in the dashboard
- No contextual search — users can't ask about the document they're looking at
- Intelligence data (department spend, compliance gaps, expiring contracts) is computed on the backend but **not surfaced** in the UI
- The search box on the documents page is purely keyword-based client-side filtering

**Result:** The most powerful feature of the system — AI-powered Q&A over 1,375 contracts — is invisible.

---

## 2. Design Principles

1. **Chat is ambient, not destination** — Users shouldn't have to navigate away to ask a question. The panel floats alongside whatever they're doing.
2. **Context flows into conversation** — When a user opens chat from a document detail page, the chat should know which document they're looking at.
3. **Intelligence surfaces proactively** — Don't wait for users to ask; show insights where they're relevant (expiring contracts on dashboard, compliance gaps on detail pages).
4. **Search and chat are one interaction** — The search box in the documents page should be the same brain as the chatbot. Type a natural language query, get smart results.
5. **Progressive disclosure** — Quick answers first, drill-down available. Don't overwhelm.

---

## 3. UX Touchpoints — Where Chat & Intelligence Live

### 3.1 Persistent Chat FAB (Floating Action Button)

**Location:** Bottom-right corner of every dashboard page
**Behavior:** Opens the slide-out `ChatPanel`
**Design:**

```
┌─────────────────────────────────────────────────────────┐
│  Sidebar  │          Page Content                       │
│           │                                             │
│           │                                             │
│           │                                             │
│           │                                             │
│           │                                        ┌───┐│
│           │                                        │ 💬││
│           │                                        └───┘│
└─────────────────────────────────────────────────────────┘
```

- Circular button, 56px, primary blue (#4F8EF7)
- MessageSquare icon from Lucide
- Subtle pulse animation on first visit (then stops)
- Badge with unread indicator if system has proactive insights
- Click opens ChatPanel (380px slide-in from right)
- Panel stays open across page navigation (state in context)

### 3.2 Document Detail — Contextual "Ask About This Document"

**Location:** Document detail page, right pane toolbar (above OCR text viewer)
**Behavior:** Opens ChatPanel with document context pre-loaded

```
┌──────────────────────┬──────────────────────────┐
│  Extracted Fields     │  [Zoom] [Print] [Ask AI] │
│  ───────────────      │  ┌─────────────────────┐ │
│  Vendor: Acme Corp    │  │  OCR Text Preview    │ │
│  Amount: $2.5M        │  │  with highlights     │ │
│  Expires: 2026-06-15  │  │                      │ │
│  ...                  │  │                      │ │
└──────────────────────┴──────────────────────────┘
```

- "Ask AI" button (Sparkles icon) in the document toolbar
- Opens ChatPanel with system message: *"I'm looking at [Document Title] by [Vendor]. What would you like to know?"*
- Pre-populates context so the LLM knows which document is active
- Suggested quick questions appear as chips:
  - "Summarize this contract"
  - "Any compliance risks?"
  - "When does this expire?"
  - "Compare to similar contracts"

### 3.3 Smart Search Bar — Documents Page

**Location:** Replace the existing keyword search box on the Unified Portfolio page
**Behavior:** Hybrid — filters the table for simple queries, opens chat for complex ones

```
┌──────────────────────────────────────────────────────────┐
│  Unified Portfolio                                        │
│  ┌──────────────────────────────────────────────────────┐│
│  │ 🔍  Search documents, ask questions...        [⏎]  ││
│  │     Try: "water contracts over $1M" or "DPU spend"  ││
│  └──────────────────────────────────────────────────────┘│
│  Source: [All ▾]  Department: [All ▾]  Status: [All ▾]   │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Vendor         Source   Dept    Value    Expires    │ │
│  │  ...                                                │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

- When input looks like a natural language question (contains "?", "how", "what", "which", "show me", "find", "total", etc.), show a blue "Ask AI" chip
- Pressing Enter on a natural question opens the ChatPanel with that query pre-filled and auto-sent
- Simple keyword inputs still filter the table as before
- Placeholder text rotates through example queries

### 3.4 Dashboard Overview — Intelligence Cards

**Location:** Dashboard home page, below the existing KPI cards
**Behavior:** Proactive intelligence from the `/intelligence/*` endpoints

```
┌─────────────────────────────────────────────────────────┐
│  [$3.5B]  Active Value  │  [7] Expiring 90d  │  [1,375]│
├─────────────────────────┴─────────────────────┴─────────┤
│                                                          │
│  ┌─ Intelligence ──────────────────────────────────────┐│
│  │                                                      ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          ││
│  │  │Compliance│  │ Vendor   │  │Sole-Source│          ││
│  │  │  Gaps    │  │  Risk    │  │  Review   │          ││
│  │  │          │  │          │  │           │          ││
│  │  │ 12 docs  │  │ 8 vendors│  │ 5 over    │          ││
│  │  │ missing  │  │ multi-   │  │ $50K need │          ││
│  │  │ fields   │  │ contract │  │ review    │          ││
│  │  └──────────┘  └──────────┘  └──────────┘          ││
│  │                                                      ││
│  │  [Ask ContractIQ about these findings →]             ││
│  └──────────────────────────────────────────────────────┘│
│                                                          │
│  ┌─ Urgent Expirations ─────┐  ┌─ Contract Insights ──┐│
│  │  (existing table)         │  │  (existing timeline)  ││
│  └───────────────────────────┘  └───────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

- 3 intelligence cards powered by the new backend endpoints
- Each card is clickable → opens ChatPanel with a pre-formed question
  - Compliance Gaps → "Which contracts have compliance gaps?"
  - Vendor Risk → "Which vendors have the highest contract concentration?"
  - Sole-Source → "Show me sole-source contracts over $50K"
- "Ask ContractIQ" link opens the panel for freeform follow-up
- Cards show real counts from `/intelligence/*` endpoints, polled every 30s

### 3.5 Analytics Page — Department Spend Intelligence

**Location:** Analytics page, new section below existing KPI cards
**Behavior:** Visual department spend breakdown from `/intelligence/department-spend`

```
┌──────────────────────────────────────────────────────────┐
│  Analytics                                                │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                    │
│  │Total │ │By    │ │Value │ │Today │                    │
│  │Docs  │ │Type  │ │      │ │      │                    │
│  └──────┘ └──────┘ └──────┘ └──────┘                    │
│                                                          │
│  ┌─ Department Spend ──────────────────────────────────┐│
│  │  PUBLIC_UTILITIES     ████████████████████  $3.5B    ││
│  │  PUBLIC_WORKS         ██████████           $1.5B    ││
│  │  PROCUREMENT          ███                  $276M    ││
│  │  HUMAN_RESOURCES      ██                   $230M    ││
│  │  PUBLIC_SAFETY        ██                   $212M    ││
│  │  ...                                                ││
│  │                                                      ││
│  │  Click any department to explore in ContractIQ →     ││
│  └──────────────────────────────────────────────────────┘│
│                                                          │
│  ┌─ Risk Summary ──────────────────────────────────────┐│
│  │  (existing expiring contracts section)               ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

- Horizontal bar chart showing spend per department
- Click a department bar → opens ChatPanel with "Tell me about [department] contracts"
- Shows document count + total value per department

### 3.6 Governance Page — Compliance Chat

**Location:** Governance/validation rules page
**Behavior:** Contextual compliance questions

- Add "Ask about compliance" button in the governance header
- Opens ChatPanel with compliance-focused prompt
- Suggested questions:
  - "Which contracts are missing MBE/WBE certification?"
  - "Federal funding contracts without compliance flags?"
  - "Contracts over $100K without insurance requirements?"

---

## 4. User Stories

### Epic: Chat Integration (CH)

#### CH-1: Mount ChatPanel in Dashboard Layout
**As a** user on any dashboard page,
**I want** to access the chat panel without navigating away,
**So that** I can ask questions while reviewing documents.

**Acceptance Criteria:**
- [ ] `ChatPanelProvider` wraps the dashboard layout
- [ ] `ChatPanel` renders (hidden by default) on all dashboard pages
- [ ] Chat FAB (floating action button) visible bottom-right on all pages
- [ ] Clicking FAB opens/closes the panel
- [ ] Panel persists open state across page navigation
- [ ] Panel slides in/out smoothly (existing animation)

**Files:**
- `procurement/frontend/src/app/dashboard/layout.tsx` — wrap with provider, add FAB
- `procurement/frontend/src/components/ChatPanelContext.tsx` — no changes needed

**Size:** S (1-2 hours)

---

#### CH-2: Contextual Chat from Document Detail
**As an** analyst reviewing a specific document,
**I want** to ask AI questions about that document,
**So that** I can understand risks and details without switching context.

**Acceptance Criteria:**
- [ ] "Ask AI" button (Sparkles icon) in document detail toolbar
- [ ] Opens ChatPanel with document context pre-loaded
- [ ] System message identifies the active document by title and vendor
- [ ] Suggested quick-question chips appear (Summarize, Risks, Expiry, Compare)
- [ ] Clicking a chip sends that question automatically
- [ ] Chat answer references the correct document

**Files:**
- `procurement/frontend/src/app/dashboard/documents/[id]/page.tsx` — add toolbar button
- `procurement/frontend/src/components/ChatPanel.tsx` — accept optional `documentContext` prop
- `procurement/frontend/src/components/ChatPanelContext.tsx` — add `openWithContext(context)` method
- `procurement/frontend/src/lib/api.ts` — extend `sendChatMessage` to accept optional context

**Size:** M (2-3 hours)

---

#### CH-3: Smart Search Bar on Documents Page
**As a** user browsing the document portfolio,
**I want** the search bar to understand natural language queries,
**So that** I can find documents by meaning, not just keywords.

**Acceptance Criteria:**
- [ ] Search bar detects natural language patterns (?, "how", "which", "total", "find", "show")
- [ ] Natural language queries show a blue "Ask AI" action chip
- [ ] Pressing Enter or clicking chip opens ChatPanel with query pre-sent
- [ ] Simple keyword queries still filter the table as before
- [ ] Placeholder text shows example queries (rotates every 5s)

**Files:**
- `procurement/frontend/src/app/dashboard/documents/page.tsx` — enhance search bar
- `procurement/frontend/src/components/ChatPanelContext.tsx` — add `openWithQuery(query)` method

**Size:** S (1-2 hours)

---

### Epic: Intelligence Dashboard (IN)

#### IN-1: Intelligence Cards on Dashboard Home
**As a** supervisor or analyst,
**I want** to see proactive intelligence insights on the dashboard,
**So that** I can identify risks and opportunities at a glance.

**Acceptance Criteria:**
- [ ] 3 intelligence cards below KPI row: Compliance Gaps, Vendor Concentration, Sole-Source Review
- [ ] Cards show real counts from `/intelligence/*` endpoints
- [ ] Cards are clickable → open ChatPanel with relevant pre-formed question
- [ ] "Ask ContractIQ" link below cards opens freeform chat
- [ ] Data refreshes every 30 seconds (TanStack Query polling)
- [ ] Loading skeleton while fetching
- [ ] Cards match existing design system (beige bg, subtle borders, #0F2537 text)

**Files:**
- `procurement/frontend/src/app/dashboard/page.tsx` — add intelligence section
- `procurement/frontend/src/lib/api.ts` — add `fetchComplianceGaps()`, `fetchVendorConcentration()`, `fetchSoleSourceReview()` functions
- `procurement/frontend/src/lib/types.ts` — add intelligence response types

**Size:** M (2-3 hours)

---

#### IN-2: Department Spend Visualization on Analytics
**As a** supervisor reviewing portfolio performance,
**I want** to see contract spend broken down by department,
**So that** I can identify where the budget is concentrated.

**Acceptance Criteria:**
- [ ] Horizontal bar chart or treemap showing spend per department
- [ ] Shows document count + total value per department
- [ ] Clicking a department opens ChatPanel with "Tell me about [dept] contracts"
- [ ] Data from `/intelligence/department-spend` endpoint
- [ ] Sorted by total value descending
- [ ] Matches analytics page design system

**Files:**
- `procurement/frontend/src/app/dashboard/analytics/page.tsx` — add department spend section
- `procurement/frontend/src/lib/api.ts` — add `fetchDepartmentSpend()` function
- `procurement/frontend/src/lib/types.ts` — add `DepartmentSpend` type

**Size:** M (2-3 hours)

---

#### IN-3: Expiring Contracts Intelligence Widget
**As a** user on the dashboard,
**I want** the expiring contracts section to be powered by the intelligence endpoint,
**So that** I get accurate, real-time expiration data with AI context.

**Acceptance Criteria:**
- [ ] Dashboard "Urgent Expirations" table uses `/intelligence/expiring?days=90`
- [ ] Each row has an "Ask AI" icon that opens chat with "Tell me about this contract's expiration"
- [ ] Count badge on the KPI card matches the intelligence endpoint count
- [ ] Fallback to existing query if intelligence endpoint fails

**Files:**
- `procurement/frontend/src/app/dashboard/page.tsx` — wire up intelligence endpoint

**Size:** S (1 hour)

---

### Epic: Chat UX Polish (CP)

#### CP-1: Chat Intent Badges and Enhanced Sources
**As a** user chatting with ContractIQ,
**I want** to see what kind of query the AI performed,
**So that** I trust the answer and understand how it was found.

**Acceptance Criteria:**
- [ ] Chat response shows intent badge (e.g., "Semantic Search", "Aggregation", "Compliance Check")
- [ ] Source chips show relevance score as a mini bar or percentage
- [ ] Sources with captions show a preview snippet below the chip
- [ ] Hovering a source chip shows document type + department

**Files:**
- `procurement/frontend/src/components/ChatPanel.tsx` — enhance message rendering
- `procurement/frontend/src/lib/types.ts` — extend ChatResponse with `intent` and `snippet`
- `procurement/backend/app/schemas/document.py` — add `intent` and `snippet` to ChatResponse schema

**Size:** M (2-3 hours)

---

#### CP-2: Suggested Questions / Quick Actions
**As a** first-time user opening the chat,
**I want** to see suggested questions I can ask,
**So that** I understand what the AI can do and get started quickly.

**Acceptance Criteria:**
- [ ] Empty chat state shows 4-6 suggested question chips
- [ ] Chips are context-aware (different on dashboard vs document detail vs analytics)
- [ ] Clicking a chip sends the question immediately
- [ ] After first message, chips disappear and full chat UI takes over
- [ ] Suggested questions:
  - Dashboard: "What contracts expire this month?", "Department with highest spend?", "Any compliance issues?"
  - Document detail: "Summarize this contract", "Any risks?", "Similar contracts?"
  - Analytics: "Spending trends by department?", "Vendor concentration risk?"

**Files:**
- `procurement/frontend/src/components/ChatPanel.tsx` — add suggested questions section
- `procurement/frontend/src/components/ChatPanelContext.tsx` — pass page context for relevant suggestions

**Size:** S (1-2 hours)

---

#### CP-3: Chat History Persistence
**As a** user who had a productive chat conversation,
**I want** my chat history to persist across page navigations,
**So that** I don't lose context when switching between documents.

**Acceptance Criteria:**
- [ ] Chat messages persist in ChatPanelContext state across page navigations
- [ ] Conversation ID is maintained for multi-turn context
- [ ] "New Conversation" button to clear and start fresh
- [ ] Last 50 messages kept in memory (no backend persistence needed for hackathon)

**Files:**
- `procurement/frontend/src/components/ChatPanelContext.tsx` — lift message state into context
- `procurement/frontend/src/components/ChatPanel.tsx` — read messages from context

**Size:** S (1 hour)

---

### Epic: Governance Chat (GC)

#### GC-1: Compliance-Focused Chat on Governance Page
**As a** supervisor managing validation rules,
**I want** to ask the AI about compliance patterns,
**So that** I can create better rules based on actual document data.

**Acceptance Criteria:**
- [ ] "Ask about compliance" button in governance page header
- [ ] Opens ChatPanel with compliance context
- [ ] Suggested questions focus on compliance patterns
- [ ] Can ask "Which contracts violate rule X?" and get relevant results

**Files:**
- `procurement/frontend/src/app/dashboard/governance/page.tsx` — add chat button

**Size:** S (1 hour)

---

## 5. Implementation Priority (Hackathon Sequence)

| Priority | Story | Size | Cumulative Time | Impact |
|----------|-------|------|-----------------|--------|
| **P0** | CH-1: Mount ChatPanel + FAB | S | 1-2h | Unlocks all chat features |
| **P0** | CP-2: Suggested questions | S | 2-3h | Users know what to ask |
| **P0** | CP-3: Chat history persistence | S | 3-4h | Conversation continuity |
| **P1** | IN-1: Intelligence cards | M | 5-6h | Dashboard value prop |
| **P1** | CH-2: Contextual document chat | M | 7-8h | Killer demo moment |
| **P1** | IN-2: Department spend chart | M | 9-10h | Analytics depth |
| **P2** | CH-3: Smart search bar | S | 10-11h | Power users |
| **P2** | CP-1: Intent badges + sources | M | 12-13h | Trust + transparency |
| **P2** | IN-3: Expiring intelligence | S | 13-14h | Data freshness |
| **P3** | GC-1: Governance chat | S | 14-15h | Compliance workflow |

**Minimum demo-ready:** P0 stories (3-4 hours) — chat works everywhere with suggested questions
**Full experience:** P0 + P1 (8-10 hours) — intelligence dashboard + contextual document chat
**Polish:** All stories (14-15 hours)

---

## 6. API Integration Map

| Frontend Component | Backend Endpoint | Polling |
|---|---|---|
| ChatPanel | `POST /api/v1/chat` | On send |
| Intelligence: Compliance Gaps | `GET /api/v1/intelligence/compliance-gaps` | 30s |
| Intelligence: Vendor Risk | `GET /api/v1/intelligence/vendor-concentration` | 30s |
| Intelligence: Sole-Source | `GET /api/v1/intelligence/sole-source-review` | 30s |
| Intelligence: Department Spend | `GET /api/v1/intelligence/department-spend` | 30s |
| Intelligence: Expiring | `GET /api/v1/intelligence/expiring?days=90` | 30s |
| Admin: Reindex | `POST /api/v1/admin/reindex` | Manual |

---

## 7. Design Tokens (Consistency with Existing System)

```
Chat FAB:
  bg: #4F8EF7 (primary blue)
  hover: #3D7CE5
  icon: white, 24px MessageSquare
  size: 56px circle
  shadow: 0 4px 12px rgba(79, 142, 247, 0.3)
  position: fixed, bottom-right, 24px margin

Intelligence Cards:
  bg: white
  border: 1px solid #E7E5E4
  border-radius: 12px
  padding: 20px
  heading: #0F2537, 14px, Bricolage Grotesque 600
  value: #0F2537, 28px, Bricolage Grotesque 700
  subtext: #A8A29E, 12px, DM Sans 400
  hover: subtle shadow elevation

Intent Badges:
  semantic_search: bg #EFF6FF, text #1E40AF
  aggregation: bg #F0FDF4, text #166534
  compliance_check: bg #FEF2F2, text #991B1B
  expiration_alert: bg #FFFBEB, text #92400E
  filter_list: bg #F5F3FF, text #5B21B6
  general_knowledge: bg #F1F5F9, text #475569

Suggested Question Chips:
  bg: #F7F5F2
  border: 1px solid #E7E5E4
  text: #292524, 13px, DM Sans 500
  hover: bg #E7E5E4
  border-radius: 20px
  padding: 8px 16px
```

---

## 8. Demo Script (Chat-Focused)

**Scene 1 — Dashboard Intelligence (30s)**
> "When staff log in, they immediately see intelligence insights — 12 contracts with compliance gaps, 8 vendors with concentration risk, and 5 sole-source contracts needing review."

**Scene 2 — Natural Language Search (30s)**
> "Staff can ask questions in plain English. Let me ask: 'What's the total contract value for water services?'"
> *Chat opens, shows aggregation result with department breakdown*

**Scene 3 — Contextual Document Chat (30s)**
> "Let's look at a specific contract. I can click 'Ask AI' and it already knows I'm looking at this stormwater engineering contract."
> *Clicks "Any compliance risks?" chip → AI responds with specific findings*

**Scene 4 — Semantic Discovery (30s)**
> "What makes this powerful is semantic understanding. 'Water infrastructure' finds stormwater, wastewater, and utility engineering contracts — not just exact keyword matches."

---

## 9. ChatResponse Schema Enhancement (Backend)

To support intent badges and snippets in the frontend, extend the response:

```python
# schemas/document.py — ChatResponse additions
class ChatSourceSchema(BaseModel):
    document_id: UUID
    title: str | None = None
    relevance: float
    snippet: str | None = None  # NEW — extractive caption from search

class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSourceSchema]
    conversation_id: str
    intent: str | None = None  # NEW — query classification for transparency
```

This requires a minor backend change to pass `intent` and `caption` through from the search client.
