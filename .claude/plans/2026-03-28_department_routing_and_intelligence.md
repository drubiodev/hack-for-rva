# ContractIQ — Department Routing & Intelligence Extraction

> Sprint plan for automatic department tagging, document routing, and extracting high-value intelligence that reduces cognitive load on City staff.

---

## Context

City of Richmond has 1,362+ contracts spanning dozens of departments. Today, every uploaded contract lands in a single undifferentiated list. Staff must manually read each document to figure out which department owns it, what compliance requirements apply, and what risks exist.

**Analysis of 10 real Richmond contracts reveals clear patterns:**

| Department Cluster | Contracts | Signals in Text |
|---|---|---|
| Public Works / Transportation | 4 of 10 | "sidewalk", "paving", "VDOT", "road and bridge specifications", "erosion", "traffic control" |
| Public Safety / Law Enforcement | 2 of 10 | "license plate recognition", "Flock Safety", "audio detection", "law enforcement" |
| Finance / Audit / Risk | 2 of 10 | "audit services", "financial statements", "workers' compensation", "claims administration" |
| Information Technology | 1 of 10 | "CAMA system", "software", "SaaS", "subscription", "license agreement" |
| Planning & Development | 1 of 10 | "elevator inspection", "building code", "VUSBC" |

**Additional intelligence not currently extracted but highly valuable:**
- MBE/WBE participation requirements (present in 6 of 10 contracts)
- Insurance minimums and types ($1M–$2M liability common)
- Bond requirements and amounts (performance + payment bonds)
- Federal funding flags (Davis-Bacon wages, VDOT funding)
- Cooperative purchasing vehicle (OMNIA Partners, piggyback contracts)
- Liquidated damages rates ($600/day in sidewalk contract)
- Subcontractor compliance requirements
- Personnel certification requirements
- Geographic scope (citywide vs. specific neighborhoods)
- Renewal terms structure (auto-renew vs. option years)

These data points currently exist buried in OCR text. Extracting them as structured fields would let staff filter, sort, and prioritize without reading full documents.

---

## Sprint Stories — MUST-HAVE

### S15: AI Department Tagging & Primary Owner Assignment

**As a** procurement analyst reviewing 50 new contracts,
**I want** each document automatically tagged with relevant department(s) and a primary department owner,
**so that** I can filter my queue to only my department's contracts.

**Problem:** The existing `issuing_department` field captures who *issued* the document, but not which operational department(s) the work *serves*. A sidewalk contract issued by Procurement actually belongs to Public Works. Staff must read the scope to figure out routing.

**Implementation:**
- Add new fields to the extraction schema in `extractor.py`:
  - `department_tags`: array of department codes (e.g., `["PUBLIC_WORKS", "TRANSPORTATION"]`)
  - `primary_department`: single department code for the primary owner
  - `department_confidence`: confidence score 0.0–1.0
- Define a canonical department taxonomy (enum) based on City of Richmond org structure:
  ```
  PUBLIC_WORKS, TRANSPORTATION, PUBLIC_SAFETY, FINANCE,
  INFORMATION_TECHNOLOGY, PLANNING_DEVELOPMENT, PUBLIC_UTILITIES,
  PARKS_RECREATION, HUMAN_RESOURCES, RISK_MANAGEMENT,
  COMMUNITY_DEVELOPMENT, CITY_ASSESSOR, PROCUREMENT, OTHER
  ```
- Add matching columns to `ExtractedFields` model: `department_tags` (JSONB array), `primary_department` (String)
- Update the LLM extraction prompt to include department classification instructions with examples:
  - "Sidewalk repair, paving, road construction → PUBLIC_WORKS"
  - "License plate cameras, body cameras, police equipment → PUBLIC_SAFETY"
  - "Audit services, financial statements → FINANCE"
  - "Software systems, SaaS, IT equipment → INFORMATION_TECHNOLOGY"
  - "Elevator inspections, building permits → PLANNING_DEVELOPMENT"
  - "Workers' comp, liability claims, insurance → RISK_MANAGEMENT"
- LLM should assign multiple tags when a contract spans departments (e.g., a VDOT-funded sidewalk project: `["PUBLIC_WORKS", "TRANSPORTATION"]`)

**Files:** `extractor.py`, `models/document.py`, `schemas/`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] Contract 25000005766 (sidewalk) tagged `PRIMARY: PUBLIC_WORKS`, tags include `PUBLIC_WORKS` and `COMMUNITY_DEVELOPMENT`
- [ ] Contract 24000006048 (Flock cameras) tagged `PRIMARY: PUBLIC_SAFETY`
- [ ] Contract 22000008081 (audit) tagged `PRIMARY: FINANCE`
- [ ] Contract 23000012317 (CAMA system) tagged `PRIMARY: INFORMATION_TECHNOLOGY` or `CITY_ASSESSOR`
- [ ] Contracts can have 1–3 department tags; exactly 1 primary department
- [ ] Department tags stored in `extracted_fields.department_tags` as JSONB array
- [ ] All existing backend tests pass
- [ ] `npx tsc --noEmit` passes

---

### S16: MBE/WBE & Compliance Flags Extraction

**As a** procurement supervisor reviewing contracts for equity compliance,
**I want** MBE/WBE participation requirements and other compliance flags automatically extracted,
**so that** I can quickly identify which contracts have diversity requirements and track compliance.

**Problem:** 6 of 10 sample contracts contain MBE/WBE participation requirements, but this isn't extracted as a structured field. Staff must search through 50+ page documents to find the clause. Same issue for Davis-Bacon wage requirements (federal funding), drug-free workplace clauses, and ADA compliance.

**Implementation:**
- Add new fields to extraction schema in `extractor.py`:
  - `mbe_wbe_required`: boolean — whether MBE/WBE participation is required
  - `mbe_wbe_details`: string — percentage targets, certification requirements, or "N/A"
  - `federal_funding`: boolean — whether federal funds are involved (triggers Davis-Bacon, Buy America, EEO)
  - `compliance_flags`: array of strings from enum: `["MBE_WBE", "DAVIS_BACON", "ADA", "DRUG_FREE_WORKPLACE", "OSHA", "VDOT_STANDARDS", "ENVIRONMENTAL"]`
- Add matching columns to `ExtractedFields` model
- Add validation rule `COMPLIANCE_MISSING` (warning severity): flag contracts over $100K that have *no* MBE/WBE clause detected — unusual for City contracts of that size

**Files:** `extractor.py`, `models/document.py`, `validation/engine.py`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Contract 25000005766 (sidewalk, $676K) extracts `mbe_wbe_required: true`
- [ ] Contract 23000004767 (VDOT road) extracts `federal_funding: true`, `compliance_flags` includes `DAVIS_BACON`
- [ ] Contract 24000006048 (Flock cameras, $91K) extracts `drug_free_workplace` in compliance flags
- [ ] A $200K contract with no MBE clause triggers `COMPLIANCE_MISSING` validation warning
- [ ] All existing backend tests pass

---

### S17: Insurance & Bonding Intelligence Extraction

**As a** risk management officer reviewing contract compliance,
**I want** insurance minimums, bond requirements, and liquidated damages automatically extracted as structured data,
**so that** I can quickly verify vendor compliance and assess financial exposure.

**Problem:** Insurance requirements ($1M–$2M general liability), performance bonds, and liquidated damages rates are buried deep in contract text (usually pages 20–40). Risk Management currently reads every contract manually to extract these figures. The existing `insurance_required` and `bond_required` fields are just booleans — they don't capture the amounts.

**Implementation:**
- Add new fields to extraction schema in `extractor.py`:
  - `insurance_general_liability_min`: number — minimum general liability coverage in dollars (e.g., 2000000)
  - `insurance_auto_liability_min`: number — minimum auto liability coverage
  - `insurance_professional_liability_min`: number — minimum professional/E&O coverage
  - `workers_comp_required`: boolean
  - `performance_bond_amount`: number or null — bond amount in dollars (often equals contract amount)
  - `payment_bond_amount`: number or null
  - `liquidated_damages_rate`: string or null — e.g., "$600 per calendar day"
- Add matching columns to `ExtractedFields` model
- Add validation rule `BOND_AMOUNT_MISMATCH` (warning): flag when `performance_bond_amount` doesn't equal `total_amount` for construction contracts (standard City requirement)

**Files:** `extractor.py`, `models/document.py`, `validation/engine.py`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Contract 25000005766 extracts `insurance_general_liability_min: 2000000`, `liquidated_damages_rate: "$600 per calendar day"`
- [ ] Contract 22000008081 (audit) extracts `insurance_professional_liability_min: 1000000`
- [ ] Construction contract with bond != total_amount triggers `BOND_AMOUNT_MISMATCH` warning
- [ ] Non-construction contracts (IT, audit) don't trigger bond mismatch
- [ ] All existing backend tests pass

---

### S18: Cooperative Purchasing & Procurement Vehicle Detection

**As a** procurement analyst evaluating contract terms,
**I want** the system to automatically detect cooperative purchasing agreements (piggyback contracts),
**so that** I know which contracts leverage pre-negotiated pricing and which are sole-source.

**Problem:** 2 of 10 sample contracts (both Flock Safety) are awarded through OMNIA Partners cooperative purchasing, piggybacking on Cobb County Contract #23-6692-03. This significantly affects pricing, renewal terms, and competitive bidding requirements. Currently invisible in extracted data.

**Implementation:**
- Add new fields to extraction schema in `extractor.py`:
  - `procurement_method`: string from enum — `"COMPETITIVE_BID"`, `"COOPERATIVE_PURCHASE"`, `"SOLE_SOURCE"`, `"EMERGENCY"`, `"RFP"`, `"OTHER"`
  - `cooperative_contract_ref`: string or null — the parent contract identifier (e.g., "OMNIA Partners / Cobb County #23-6692-03")
  - `prequalification_required`: boolean
- Add matching columns to `ExtractedFields` model

**Files:** `extractor.py`, `models/document.py`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Contract 24000006048 extracts `procurement_method: "COOPERATIVE_PURCHASE"`, `cooperative_contract_ref` contains "OMNIA" and "Cobb County"
- [ ] Contract 25000005766 (IFB sidewalk) extracts `procurement_method: "COMPETITIVE_BID"`, `prequalification_required: false`
- [ ] Contract 22000008081 (audit RFP) extracts `procurement_method: "RFP"`
- [ ] All existing backend tests pass

---

### S19: Dashboard Department Filter & Routing View

**As a** department administrator logging into ContractIQ,
**I want** to filter the document list by department tags,
**so that** I only see contracts relevant to my department.

**Problem:** The dashboard shows all 1,362+ documents in a single list. A Public Works admin must scroll through IT contracts, audit contracts, and police equipment contracts to find their sidewalk projects. No filtering by department exists.

**Implementation:**
- Add department filter dropdown to the dashboard list page (`page.tsx`)
  - Multi-select dropdown using shadcn `Select` or `Combobox` component
  - Filter options populated from the department taxonomy enum
  - "All Departments" default
  - Filter applied client-side initially (TanStack Query filter), with backend `?department=` query param for server-side filtering
- Add department badge/chip on each document card in the list
  - Color-coded by department (e.g., Public Works = orange, Public Safety = blue, Finance = green)
  - Show primary department as main badge, additional tags as smaller secondary badges
- Add `department` query parameter to the list documents API endpoint

**Files:** `frontend/src/app/dashboard/page.tsx`, `backend/app/api/router.py`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] Department filter dropdown appears on dashboard with all 14 department options
- [ ] Selecting "PUBLIC_WORKS" filters list to only contracts tagged with that department
- [ ] Each document card shows a color-coded department badge
- [ ] Multi-department contracts show primary badge prominently + secondary tags
- [ ] "All Departments" shows unfiltered list
- [ ] `npx tsc --noEmit` passes
- [ ] Backend `GET /api/v1/documents?department=PUBLIC_WORKS` returns filtered results

---

### S20: Contract Intelligence Summary Card

**As a** procurement analyst opening a contract detail page,
**I want** a "Contract Intelligence" summary card showing all extracted risk and compliance data at a glance,
**so that** I don't have to read the full document to understand key obligations.

**Problem:** The detail page shows basic extracted fields (vendor, amount, dates) but buries critical intelligence like MBE requirements, insurance minimums, bond amounts, and liquidated damages in the raw extraction JSON. Staff still have to read the PDF for these.

**Implementation:**
- Add a "Contract Intelligence" collapsible card on the document detail page, below the existing extracted fields section
- Sections within the card:
  - **Department Routing:** Primary department badge + secondary tags
  - **Compliance:** MBE/WBE status, federal funding flag, compliance flags as chips
  - **Financial Risk:** Insurance minimums table, bond amounts, liquidated damages rate
  - **Procurement:** Method, cooperative contract reference, prequalification status
  - **Geographic Scope:** Extracted geographic information (future: map pin)
- Each field shows source confidence indicator (green/yellow/red dot)
- "Verify in Original" link next to each field that scrolls to the relevant page in the PDF viewer (if available)

**Files:** `frontend/src/app/dashboard/documents/[id]/page.tsx`, `frontend/src/lib/types.ts`

**Effort:** 2 hours

**Acceptance Criteria:**
- [ ] Intelligence card renders on detail page for extracted documents
- [ ] Department badges are color-coded and clickable (filters dashboard to that department)
- [ ] Compliance flags show as chips (green = present, gray = not detected)
- [ ] Insurance/bond amounts formatted as currency
- [ ] Card is collapsible (default expanded)
- [ ] Documents without intelligence data show "Intelligence extraction pending" state
- [ ] `npx tsc --noEmit` passes

---

## Sprint Stories — NICE-TO-HAVE

### S21: Geographic Scope Extraction & Neighborhood Tagging

**As a** a city council member reviewing contracts in their district,
**I want** contracts tagged with specific Richmond neighborhoods or geographic areas,
**so that** I can see what work is happening in my district.

**Problem:** Contract 25000005766 lists 10+ specific street addresses and references "Windsor Farms" by name. This geographic intelligence is lost after OCR — no structured extraction captures it.

**Implementation:**
- Add new fields to extraction schema:
  - `geographic_scope`: string — `"CITYWIDE"`, `"DISTRICT"`, `"NEIGHBORHOOD"`, `"SITE_SPECIFIC"`
  - `locations`: array of strings — specific addresses, neighborhoods, or landmarks mentioned
  - `council_district`: string or null — if determinable from addresses
- Maintain a lightweight Richmond neighborhood lookup (10–15 major neighborhoods mapped to council districts)

**Files:** `extractor.py`, `models/document.py`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Contract 25000005766 extracts locations including "Windsor Farms", "Bryan Park Ave", "W Main St"
- [ ] Contract 20000003712 (elevator inspection) extracts `geographic_scope: "CITYWIDE"`
- [ ] Contracts with no location info default to `geographic_scope: "CITYWIDE"`
- [ ] All existing backend tests pass

---

### S22: Vendor Risk Intelligence

**As a** procurement supervisor evaluating vendor performance,
**I want** personnel and certification requirements automatically extracted,
**so that** I can verify vendor qualifications without reading the full contract.

**Problem:** Contracts specify detailed personnel requirements (e.g., "minimum 2 full-time liability adjusters with 3 years' experience", "Licensed QEI certification") and response time SLAs (e.g., "3-hour accident response", "48-hour personnel replacement"). These are key vendor management data points currently buried in text.

**Implementation:**
- Add new fields to extraction schema:
  - `personnel_requirements`: string or null — summary of staffing/certification requirements
  - `response_time_sla`: string or null — key SLA commitments (e.g., "3-hour emergency response")
  - `subcontractor_restrictions`: string or null — notable restrictions on subcontracting
- Add matching columns to `ExtractedFields` model

**Files:** `extractor.py`, `models/document.py`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Contract 20000003712 extracts `personnel_requirements` mentioning "QEI certification"
- [ ] Contract 24000012493 extracts `response_time_sla` mentioning nurse triage "24/7/365"
- [ ] Contract 25000005766 extracts `personnel_requirements` mentioning "Porous Pave installation certification"
- [ ] All existing backend tests pass

---

### S23: Contract Renewal & Expiration Alerting by Department

**As a** department administrator,
**I want** to see a dashboard widget showing contracts expiring in the next 30/60/90 days filtered by my department,
**so that** I can proactively manage renewals instead of being surprised.

**Problem:** The existing reminder system is per-document. There's no department-level view that shows "Public Works has 3 contracts expiring in 30 days." Department heads don't know what's coming due.

**Implementation:**
- Add analytics endpoint: `GET /api/v1/analytics/department-expirations?department=PUBLIC_WORKS&days=90`
  - Returns count and list of contracts expiring within N days, grouped by 30/60/90 day buckets
- Add dashboard widget on the main page showing expiration counts by department
  - Color-coded urgency: red (30 days), yellow (60 days), blue (90 days)
  - Clicking a bucket navigates to filtered document list

**Files:** `backend/app/api/router.py`, `frontend/src/app/dashboard/page.tsx`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] API returns correct expiration counts grouped by department and time bucket
- [ ] Dashboard widget shows department-level expiration summary
- [ ] Clicking a count filters the document list to those contracts
- [ ] Departments with no expiring contracts show "0" (not hidden)
- [ ] `npx tsc --noEmit` passes

---

### S24: Auto-Route Notification Stub

**As a** system administrator,
**I want** the system to log a routing recommendation when a document is extracted,
**so that** future email/Slack notification integration has a trigger point.

**Problem:** Even with department tags, there's no mechanism to *notify* the right department admin. This story creates the routing decision record and extensibility point — actual notification delivery (email, Slack) is out of scope for hackathon.

**Implementation:**
- After extraction completes in `pipeline.py`, create an `ActivityLog` entry:
  - action: `"auto_routed"`
  - details: `{"primary_department": "PUBLIC_WORKS", "tags": ["PUBLIC_WORKS", "TRANSPORTATION"], "confidence": 0.92}`
  - actor_role: `"system"`
- Log at INFO level: `"Document {id} auto-routed to PUBLIC_WORKS (confidence: 0.92)"`

**Files:** `pipeline.py`

**Effort:** 20 minutes

**Acceptance Criteria:**
- [ ] After extraction, an `auto_routed` activity log entry exists with department info
- [ ] Activity log visible on document detail page timeline
- [ ] No actual notifications sent (stub only)
- [ ] All existing backend tests pass

---

## Department Taxonomy Reference

Canonical department codes derived from City of Richmond organizational structure and the 10 sample contracts:

| Code | Full Name | Signal Keywords |
|---|---|---|
| `PUBLIC_WORKS` | Department of Public Works | sidewalk, paving, road, bridge, street, curb, drainage, erosion, infrastructure |
| `TRANSPORTATION` | Department of Transportation | VDOT, traffic control, highway, corridor, signal, transit |
| `PUBLIC_SAFETY` | Public Safety / Law Enforcement | police, law enforcement, camera, surveillance, Flock, license plate, body camera, firearm |
| `FINANCE` | Department of Finance | audit, financial statement, accounting, budget, revenue |
| `RISK_MANAGEMENT` | Risk Management | workers' compensation, liability claims, insurance, loss control, TPA |
| `INFORMATION_TECHNOLOGY` | Department of IT | software, SaaS, hardware, network, computer, server, license agreement, CAMA |
| `PLANNING_DEVELOPMENT` | Planning & Development | building code, zoning, inspection, elevator, permit, VUSBC |
| `PUBLIC_UTILITIES` | Department of Public Utilities | water, sewer, gas, electric, utility, meter |
| `PARKS_RECREATION` | Parks & Recreation | park, recreation, trail, playground, athletic, pool |
| `HUMAN_RESOURCES` | Human Resources | staffing, employee, training, benefits, recruitment |
| `COMMUNITY_DEVELOPMENT` | Community Development | housing, neighborhood, community, block grant, CDBG |
| `CITY_ASSESSOR` | City Assessor | property assessment, appraisal, CAMA, valuation, real estate |
| `PROCUREMENT` | Department of Procurement | (meta — the issuing department for most contracts) |
| `OTHER` | Uncategorized | fallback for unrecognized departments |

---

## Implementation Priority Order

```
S15 Department tagging         ██████████████ 1.5h  <- Unlocks routing + filtering
S19 Dashboard department filter ██████████████ 1.5h  <- Immediate UX payoff
S16 MBE/WBE compliance flags   ████████████ 1h      <- High value for equity tracking
S17 Insurance & bonding intel   ████████████ 1h      <- Risk management visibility
S18 Procurement vehicle detect  ████████ 45m         <- Pricing context
S20 Intelligence summary card   ████████████████ 2h  <- Surfaces everything on detail page
──────────────────────────────────────────────────────
Total MUST-HAVE:               ~7.75 hours

S24 Auto-route notification     ████ 20m             <- Extensibility stub
S22 Vendor risk intelligence    ████████ 45m         <- Personnel/SLA extraction
S21 Geographic scope tagging    ████████████ 1h      <- Council district visibility
S23 Dept expiration dashboard   ██████████████ 1.5h  <- Proactive renewal management
──────────────────────────────────────────────────────
Total NICE-TO-HAVE:            ~3.5 hours
```

---

## QA Verification Plan

After implementing any story, verify:

1. **Backend tests pass:** `cd procurement/backend && .venv/bin/python -m pytest -v --tb=short`
2. **Frontend type-check:** `cd procurement/frontend && npx tsc --noEmit`
3. **Frontend build:** `cd procurement/frontend && npm run build`
4. **Extraction quality test (for S15–S18):**
   - Re-process Contract 25000005766 (sidewalk) — verify PUBLIC_WORKS tag, MBE flag, $600/day liquidated damages
   - Re-process Contract 24000006048 (Flock cameras) — verify PUBLIC_SAFETY tag, COOPERATIVE_PURCHASE method
   - Re-process Contract 22000008081 (audit) — verify FINANCE tag, $1M professional liability
5. **Dashboard test (for S19–S20):**
   - Department filter shows/hides contracts correctly
   - Intelligence card renders with real extracted data
6. **Specific acceptance criteria** listed per story above
