# ContractIQ — AI-Powered Configurable Validation & GRC Dashboard

> Sprint plan for semantic policy enforcement, department-scoped governance rules, and a dedicated GRC management interface for city officials.

---

## Context

ContractIQ currently has **13 hardcoded validation rules** in `engine.py` that run identically on every document. This works for a universal baseline, but Richmond's departments have fundamentally different risk profiles:

- **Public Works** needs bond requirements on *all* contracts (not just >$100K)
- **Finance** flags anything over $500K for extra scrutiny
- **Parks & Recreation** must verify neighborhood references match real Richmond districts
- **Procurement** wants to enforce MBE/WBE participation on contracts above a threshold

Today, none of this is configurable. A supervisor who wants stricter rules has no lever to pull — they're stuck with the same checks as every other department.

### Why semantic evaluation instead of regex/keyword matching?

City policy is written in **natural language**, not regex. A procurement officer thinks:

> "All construction contracts over $250K must include a performance bond that matches the contract value and environmental liability coverage."

A regex approach would require the officer to decompose this into field-level operators (`total_amount > 250000 AND bond_required = true AND ...`), hope the AI extracted all the right fields, and miss any nuance the fields don't capture. It's brittle, requires technical literacy, and fails on anything the extraction schema doesn't model.

**Semantic evaluation** sends the full policy statement + the document's OCR text and extracted fields to Azure OpenAI (ChatGPT 5.4 mini — already in our stack) and asks: *"Does this document comply with this policy?"* The LLM returns a structured verdict with evidence quotes from the source document. This means:

- Officers write rules in plain English — no regex, no field mapping
- Rules catch things the extraction schema doesn't model (e.g., "subcontractor flow-down clauses")
- The LLM cites specific passages from the document as evidence
- Deterministic rules (`threshold`, `required_field`, `date_window`) stay deterministic — no AI overhead for things that are simple math

### Why a GRC dashboard instead of a settings page?

Governance, Risk & Compliance is the frame city officials already think in. A "settings page" signals configuration — a GRC dashboard signals **operational control**. It needs:

- **Rule lifecycle management** — draft rules, test them against existing documents before activating, retire rules that are no longer relevant
- **Compliance posture** — at a glance, how compliant is each department's portfolio?
- **Audit trail** — who created, modified, or disabled each rule and when?
- **Rule effectiveness** — which rules trigger often? Which are just noise?

This is a dedicated section of the dashboard, not buried in settings.

### Design principles

1. **Additive, not replacement** — hardcoded rules stay as the baseline; custom rules layer on top
2. **Semantic-first, deterministic where appropriate** — use Azure OpenAI for natural-language policy rules; keep simple math rules (threshold, date, required field) deterministic
3. **Batched AI evaluation** — all semantic rules evaluated in a single LLM call per document (cost control)
4. **No new infrastructure** — rules live in the existing Azure SQL database; AI calls use the existing Azure OpenAI deployment
5. **Department matching uses existing fields** — `primary_department` and `department_tags` from ExtractedFields (already populated by the AI extractor)
6. **Supervisor-level management** — supervisors create/toggle rules via GRC dashboard; analysts see the results on document detail

---

## Data Model

### New table: `validation_rule_configs`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `name` | VARCHAR(150) | Human-readable name, e.g. "Require performance bond on construction >$250K" |
| `description` | TEXT | Full explanation of the policy intent — shown in GRC dashboard |
| `rule_type` | VARCHAR(30) | `threshold`, `required_field`, `semantic_policy`, `district_check`, `date_window` |
| `scope` | VARCHAR(20) | `global` or `department` |
| `department` | VARCHAR(100), nullable | NULL for global rules; department name for scoped rules |
| `severity` | VARCHAR(20) | `error`, `warning`, `info` |
| `status` | VARCHAR(20) | `draft`, `active`, `deprecated` — lifecycle state |
| `policy_statement` | TEXT, nullable | Natural-language policy for `semantic_policy` rules. This is the prompt sent to Azure OpenAI. |
| `field_name` | VARCHAR(100), nullable | Which extracted field this rule checks (for deterministic rules) |
| `operator` | VARCHAR(20), nullable | `gt`, `lt`, `gte`, `lte`, `eq`, `neq`, `is_empty`, `is_not_empty` |
| `threshold_value` | VARCHAR(255), nullable | Comparison value (stored as string, cast at runtime) |
| `message_template` | TEXT, nullable | Template with `{field}`, `{value}`, `{threshold}` placeholders (for deterministic rules) |
| `suggestion` | TEXT, nullable | Recommended remediation action |
| `enabled` | BOOLEAN | Default TRUE — master toggle (independent of status lifecycle) |
| `applies_to_doc_types` | JSON, nullable | NULL = all; or list like `["contract", "purchase_order"]` |
| `created_by` | VARCHAR(100) | Who created the rule |
| `created_at` | DATETIME | Auto |
| `updated_at` | DATETIME | Auto |

### New table: `validation_rule_audit_log`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `rule_id` | UUID | FK → validation_rule_configs (SET NULL on delete) |
| `rule_name` | VARCHAR(150) | Denormalized — preserved even if rule is deleted |
| `action` | VARCHAR(20) | `created`, `updated`, `toggled`, `status_changed`, `deleted` |
| `changed_by` | VARCHAR(100) | Who made the change |
| `changed_at` | DATETIME | When |
| `old_values` | JSON, nullable | Previous state (for updates) |
| `new_values` | JSON, nullable | New state (for updates) |

### Updated `validation_results` table

Add columns to existing ValidationResult model:

| Column | Type | Notes |
|--------|------|-------|
| `policy_rule_id` | UUID, nullable | FK → validation_rule_configs. NULL for hardcoded system rules. Links result to the policy that triggered it. |
| `ai_evidence` | TEXT, nullable | LLM-cited evidence quotes from the source document (for semantic rules) |
| `ai_confidence` | Numeric(3,2), nullable | LLM's confidence in the policy evaluation (0.0-1.0) |

### Richmond districts reference data

Hardcoded list in a new `procurement/backend/app/validation/districts.py`:
```python
RICHMOND_DISTRICTS = [
    "1st District", "2nd District", "3rd District", "4th District",
    "5th District", "6th District", "7th District", "8th District", "9th District"
]
RICHMOND_NEIGHBORHOODS = [
    "Church Hill", "The Fan", "Carytown", "Shockoe Bottom",
    "Jackson Ward", "Scott's Addition", "Manchester", "Oregon Hill",
    "Byrd Park", "Museum District", "Northside", "Southside",
    "East End", "West End", "Fulton", "Highland Park",
    "Woodland Heights", "Forest Hill", "Swansboro", "Gilpin Court",
    "Mosby", "Whitcomb Court", "Creighton Court", "Fairfield Court"
]
```

---

## Semantic Policy Evaluation — Architecture

### How it works

When a document is processed through the pipeline, after extraction and deterministic rule evaluation:

1. **Collect applicable semantic rules** — query `validation_rule_configs` where `rule_type = 'semantic_policy'` AND `enabled = True` AND `status = 'active'`, filtered by department scope and doc type
2. **Build a single batched prompt** — include all applicable semantic rules in one Azure OpenAI call:

```
System: You are a procurement compliance evaluator for the City of Richmond.
You will be given a document's extracted data and OCR text, along with a set of
policy rules. For each rule, determine whether the document COMPLIES, VIOLATES,
or is NOT APPLICABLE (the rule doesn't apply to this type of document).

Be precise. Cite specific passages from the document as evidence. If a rule
requires information that isn't present in the document, that is a VIOLATION
(missing required information), not NOT_APPLICABLE.

User:
## Document
- Type: {document_type}
- Vendor: {vendor_name}
- Department: {primary_department}
- Amount: ${total_amount}
- Effective: {effective_date} → Expiration: {expiration_date}

### OCR Text (excerpt — first 3000 chars + keyword windows)
{smart_truncated_ocr_text}

### Extracted Fields
{json of all extracted fields}

## Policy Rules to Evaluate

Rule 1: "{rule.name}"
Policy: {rule.policy_statement}
Severity if violated: {rule.severity}

Rule 2: ...
(up to N rules)
```

3. **Structured JSON response** (strict schema, same pattern as classifier/extractor):

```json
{
  "evaluations": [
    {
      "rule_index": 1,
      "verdict": "VIOLATES",
      "confidence": 0.92,
      "reasoning": "The contract is for road construction ($2.3M) but specifies a performance bond of only $500K, which is less than the contract value.",
      "evidence_quotes": [
        "performance bond in the amount of Five Hundred Thousand Dollars ($500,000)",
        "total contract value of Two Million Three Hundred Thousand Dollars ($2,300,000)"
      ],
      "suggestion": "Require the vendor to increase the performance bond to match the contract value of $2,300,000."
    },
    {
      "rule_index": 2,
      "verdict": "COMPLIES",
      "confidence": 0.88,
      "reasoning": "The contract includes MBE/WBE participation commitment of 15%, exceeding the 10% minimum.",
      "evidence_quotes": ["MBE/WBE participation goal: 15%"],
      "suggestion": null
    }
  ]
}
```

4. **Only VIOLATES verdicts create ValidationResult records** — COMPLIES and NOT_APPLICABLE are silently passed

### Cost control

- **Batched**: All semantic rules in a single API call per document (not one call per rule)
- **Budget**: `max_completion_tokens=800` — comparable to the existing AI consistency check (400 tokens) but allowing for multi-rule evaluation
- **Skip if no semantic rules**: If zero `semantic_policy` rules are active, no AI call is made
- **Reuse smart truncation**: Use the same `_smart_truncate()` function from S1 (resilience plan) for OCR text in the prompt
- **Token-aware rule batching**: If >10 semantic rules exist, split into batches of 10 per API call to stay within context limits

### Why not Azure AI Search for real-time rule evaluation?

Azure AI Search excels at **retrieval** (finding relevant documents from a corpus), not **evaluation** (determining if a specific document complies with a specific policy). The LLM is the right tool for evaluation because:

- It understands natural-language policy statements
- It can reason about compliance across multiple document sections
- It produces structured verdicts with evidence citations
- It's already in our stack with proven patterns

Azure AI Search *would* be the right tool for a future "retrospective scan" feature (S10) — "show me all existing documents that might violate this new rule" — but that's a nice-to-have.

---

## Sprint Stories — MUST-HAVE

### S1: Data Model — ValidationRuleConfig, Audit Log, and Result Extensions

**As a** system persisting configurable validation rules with audit history,
**I want** database tables for rule configurations and change tracking,
**so that** rules survive server restarts, link to their results, and maintain a compliance audit trail.

**Problem:** All validation logic is hardcoded. There's no database representation of configurable rules, no audit trail for policy changes, and no way to link a validation result back to the policy that triggered it.

**Implementation:**
- Add `ValidationRuleConfig` SQLAlchemy model to `procurement/backend/app/models/document.py`
  - All columns from the data model above
  - `applies_to_doc_types` as JSON column (same pattern as `department_tags`)
  - `status` defaults to `"draft"` — rules start inactive until explicitly activated
- Add `ValidationRuleAuditLog` SQLAlchemy model
  - FK to `validation_rule_configs` with SET NULL on delete (preserve history even if rule is deleted)
  - `old_values` and `new_values` as JSON columns
- Extend existing `ValidationResult` model with:
  - `policy_rule_id` (UUID, FK → validation_rule_configs, nullable)
  - `ai_evidence` (Text, nullable)
  - `ai_confidence` (Numeric(3,2), nullable)
- Add corresponding Pydantic schemas to `procurement/backend/app/schemas/document.py`:
  - `ValidationRuleConfigCreate` — input for creating rules
  - `ValidationRuleConfigUpdate` — partial update (all fields optional)
  - `ValidationRuleConfigSchema` — full response
  - `ValidationRuleAuditLogSchema` — audit log response
  - Update `ValidationResultSchema` with new fields
- Tables created automatically via `init_db()` (existing pattern)

**Files:** `models/document.py`, `schemas/document.py`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] `ValidationRuleConfig` model exists with all columns including `policy_statement`, `status` lifecycle
- [ ] `ValidationRuleAuditLog` model exists with FK to rule configs
- [ ] `ValidationResult` model has `policy_rule_id`, `ai_evidence`, `ai_confidence` columns
- [ ] Pydantic schemas for create, update, and response exist for all new models
- [ ] Tables are created on server startup via `init_db()`
- [ ] All existing backend tests pass

---

### S2: CRUD API for Validation Rules with Audit Logging

**As a** supervisor managing validation rules,
**I want** API endpoints to create, list, update, toggle, and lifecycle-manage rules,
**so that** I can configure validation behavior and every change is recorded.

**Problem:** No API exists to manage validation rules. Supervisors have no way to add, edit, or disable rules. No audit trail exists for compliance reporting.

**Implementation:**
- Add endpoints to `procurement/backend/app/api/router.py`:
  - `GET /api/v1/validation-rules` — list all rules (optional `?scope=global|department&department=X&status=draft|active|deprecated&enabled=true|false&rule_type=...`)
  - `POST /api/v1/validation-rules` — create a rule (supervisor only). New rules default to `status=draft`
  - `PATCH /api/v1/validation-rules/{id}` — update a rule (supervisor only)
  - `DELETE /api/v1/validation-rules/{id}` — soft-delete: sets `status=deprecated`, `enabled=False` (supervisor only). Hard-delete only for `draft` rules
  - `POST /api/v1/validation-rules/{id}/toggle` — quick enable/disable toggle (supervisor only)
  - `POST /api/v1/validation-rules/{id}/activate` — move from `draft` → `active` (supervisor only)
  - `POST /api/v1/validation-rules/{id}/deprecate` — move from `active` → `deprecated` (supervisor only)
  - `GET /api/v1/validation-rules/{id}/audit-log` — return change history for this rule
- Every mutation (create, update, toggle, activate, deprecate, delete) writes a `ValidationRuleAuditLog` record with before/after state
- Role check: `X-User-Role` header must be "supervisor" for mutations; analysts can read
- Validate `rule_type` is one of: `threshold`, `required_field`, `semantic_policy`, `district_check`, `date_window`
- For `semantic_policy` rules, require `policy_statement` to be non-empty
- For `threshold` rules, require `field_name`, `operator`, and `threshold_value`

**Files:** `router.py`, `openapi.yaml`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] All CRUD endpoints work and return correct schemas
- [ ] Supervisor can create, update, toggle, activate, deprecate, and delete rules
- [ ] Analyst can list and read rules but gets 403 on mutations
- [ ] List endpoint supports filtering by scope, department, status, enabled, and rule_type
- [ ] Every mutation creates an audit log entry with old/new values
- [ ] Audit log endpoint returns chronological history for a rule
- [ ] `semantic_policy` creation requires non-empty `policy_statement`
- [ ] Draft rules can be hard-deleted; active rules are soft-deprecated
- [ ] OpenAPI spec updated with all new endpoints and schemas
- [ ] All existing backend tests pass

---

### S3: Semantic Policy Evaluation Engine

**As a** validation engine processing a document,
**I want** to evaluate semantic policy rules using Azure OpenAI alongside deterministic custom rules,
**so that** natural-language policies are enforced with AI reasoning and evidence citations.

**Problem:** `validate_document()` only runs hardcoded rules. There is no mechanism to evaluate natural-language policy statements against document content.

**Implementation:**

**Part A — Deterministic custom rule evaluation:**
- Add `_evaluate_deterministic_rules(fields: dict, rules: list) -> list[dict]` to `engine.py`
- For each enabled, active rule with deterministic type, check scope:
  - `global`: always applies
  - `department`: only if document's `primary_department` or `department_tags` match rule's `department`
- Check `applies_to_doc_types`: skip if doc type not in the list (NULL = apply to all)
- Evaluate by `rule_type`:
  - **`threshold`**: Compare `fields[field_name]` against `threshold_value` using `operator` (cast numeric fields to float)
  - **`required_field`**: Check if `fields[field_name]` is present and non-empty
  - **`district_check`**: Validate that location/neighborhood references in scope_summary or OCR text match known Richmond districts/neighborhoods (using the hardcoded list from `districts.py`)
  - **`date_window`**: Check if a date field falls within N days of today (threshold_value = number of days)
- Render `message_template` with `{field}`, `{value}`, `{threshold}` substitution
- Return results with `rule_code = f"POLICY: {rule.name}"`, plus `policy_rule_id`, severity, message, field_name, suggestion

**Part B — Semantic policy evaluation (the core innovation):**
- Add `_evaluate_semantic_policies(fields: dict, ocr_text: str, rules: list) -> list[dict]` to `engine.py`
- Filter to `rule_type == 'semantic_policy'` rules only
- If zero rules, return empty list immediately (no API call)
- Build the batched prompt as described in the Architecture section:
  - System prompt: procurement compliance evaluator role
  - User prompt: document metadata + smart-truncated OCR text + extracted fields JSON + numbered policy rules
- Define strict JSON response schema `semantic_policy_evaluation`:
  ```json
  {
    "evaluations": [{
      "rule_index": int,
      "verdict": "COMPLIES" | "VIOLATES" | "NOT_APPLICABLE",
      "confidence": float (0.0-1.0),
      "reasoning": string,
      "evidence_quotes": [string],
      "suggestion": string | null
    }]
  }
  ```
- Call Azure OpenAI with `temperature=0.0`, `max_completion_tokens=800`
- For each `VIOLATES` verdict, create a validation result dict with:
  - `rule_code = f"POLICY: {rule.name}"`
  - `message` = the LLM's `reasoning`
  - `suggestion` = the LLM's `suggestion` (or fall back to rule's default suggestion)
  - `ai_evidence` = joined evidence quotes
  - `ai_confidence` = the LLM's confidence score
  - `policy_rule_id` = the rule's UUID
  - `severity` = the rule's configured severity
- If >10 semantic rules, batch into groups of 10 (separate API calls)
- Wrap in try/except: if Azure OpenAI fails, log warning and skip semantic evaluation (don't block the pipeline)
- PLACEHOLDER credential check: skip semantic evaluation if Azure OpenAI key is PLACEHOLDER

**Part C — Integration:**
- Update `validate_document()` signature to accept `custom_rules: list` and `ocr_text: str` parameters
- Call deterministic evaluation, then semantic evaluation, then combine all results
- Update `pipeline.py`:
  1. After extraction, query all enabled + active `ValidationRuleConfig` records from DB
  2. Pass them + ocr_text to `validate_document()`
  3. When saving `ValidationResult` records, include new fields (`policy_rule_id`, `ai_evidence`, `ai_confidence`)

**Files:** `engine.py`, `pipeline.py`, `validation/districts.py` (new)

**Effort:** 2.5 hours

**Acceptance Criteria:**
- [ ] **Deterministic**: `threshold` rule "total_amount > 500000" triggers warning on a $600K contract
- [ ] **Deterministic**: `required_field` rule for bond_required triggers on contract missing bond info
- [ ] **Deterministic**: `district_check` validates neighborhood references against Richmond list
- [ ] **Deterministic**: `date_window` rule "expiration within 60 days" triggers warning
- [ ] **Semantic**: A policy "All construction contracts must include environmental liability insurance" triggers on a construction contract without it, with evidence quotes from the document
- [ ] **Semantic**: A policy about MBE/WBE participation returns COMPLIES on a document that mentions 15% MBE participation
- [ ] **Semantic**: Evidence quotes are actual passages from the OCR text, not hallucinated
- [ ] **Batching**: 5 semantic rules result in 1 API call, not 5
- [ ] **Cost**: No API call is made when zero semantic rules are active
- [ ] **Resilience**: Azure OpenAI failure logs a warning but doesn't fail the pipeline
- [ ] Department-scoped rules only fire for matching departments
- [ ] Global rules fire for all documents
- [ ] Disabled rules and draft-status rules are skipped
- [ ] `applies_to_doc_types` filtering works (e.g., contracts only)
- [ ] Custom rule results appear alongside hardcoded results in ValidationResult table
- [ ] `policy_rule_id` links each result back to its source rule
- [ ] All existing backend tests pass

---

### S4: Seed Default Policy Rules for Demo

**As a** demo presenter showing the system to city judges,
**I want** pre-loaded rules — including semantic policies — that demonstrate department-specific governance,
**so that** the feature has immediate "wow factor" without manual setup.

**Problem:** An empty rules table during the demo defeats the purpose of the feature.

**Implementation:**
- Add `_seed_default_rules(session)` function to `main.py`, called during lifespan after `init_db()`
- Only seed if `validation_rule_configs` table is empty (idempotent)
- Seed these rules (all with `status="active"`, `enabled=True`):

| Name | Type | Scope | Department | Severity | Key config |
|------|------|-------|------------|----------|------------|
| High-value contract scrutiny | threshold | global | — | warning | `total_amount > 500000` |
| Require bond for Public Works | required_field | department | Public Works | error | `bond_required is_not_empty` |
| Verify Richmond district reference | district_check | global | — | warning | Checks scope_summary against district list |
| Construction environmental compliance | semantic_policy | department | Public Works | error | *"All construction contracts must include environmental liability insurance coverage and a hazardous materials handling plan if the scope involves demolition, excavation, or renovation of structures built before 1980."* |
| MBE/WBE participation for large contracts | semantic_policy | global | — | warning | *"Contracts over $50,000 should include a Minority Business Enterprise (MBE) or Women's Business Enterprise (WBE) participation plan with a specific percentage commitment. If no MBE/WBE plan is present, flag for review."* |
| Subcontractor flow-down clauses | semantic_policy | global | — | info | *"Contracts that authorize subcontracting must include flow-down clauses requiring subcontractors to meet the same insurance, bonding, and compliance requirements as the prime contractor."* |
| Contract duration reasonableness | date_window | global | — | warning | `expiration_date within 1825 days (5 years)` |
| Insurance adequacy for high-value contracts | semantic_policy | department | Finance | error | *"Contracts over $100,000 must specify general liability insurance of at least $1,000,000 per occurrence and automobile liability of at least $500,000. The City of Richmond must be named as additional insured."* |

- Also seed 2 **draft** rules (to demonstrate the lifecycle):

| Name | Type | Scope | Status | Key config |
|------|------|-------|--------|------------|
| Prevailing wage compliance | semantic_policy | global | draft | *"Publicly funded construction contracts must include prevailing wage rate requirements per the Davis-Bacon Act or Virginia prevailing wage law."* |
| Emergency procurement justification | semantic_policy | global | draft | *"Emergency procurement contracts must include a written justification explaining why competitive bidding was not feasible and the specific emergency circumstances."* |

**Files:** `main.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] On first startup with empty table, 10 rules are seeded (8 active, 2 draft)
- [ ] On subsequent startups, no duplicates are created
- [ ] Semantic policy rules have rich, realistic policy statements
- [ ] Rules span multiple types (threshold, required_field, semantic_policy, district_check, date_window)
- [ ] Rules span scopes (global and department-specific)
- [ ] Each rule creates an audit log entry with `action=created, changed_by=system`
- [ ] Rules are immediately visible via `GET /api/v1/validation-rules`
- [ ] All existing backend tests pass

---

### S5: GRC Dashboard — Policy Rules Management

**As a** supervisor responsible for procurement governance,
**I want** a dedicated Governance section in the dashboard where I can view, create, edit, toggle, and lifecycle-manage validation rules with full audit visibility,
**so that** I have operational control over the policy framework that governs document review.

**Problem:** The Settings link in the sidebar is a dead placeholder. There is no UI for policy management, no visibility into rule lifecycle, and no way to understand rule effectiveness — supervisors must manage governance blind.

**Implementation:**

**New route:** `procurement/frontend/src/app/dashboard/governance/page.tsx`

**Sidebar update:** Replace "Settings" link in `layout.tsx` with "Governance" pointing to `/dashboard/governance`. Use a Shield icon. Show for both roles (analysts see read-only view).

**Page layout — three tab sections:**

**Tab 1: Policy Rules** (default tab)
- **Header row:** "Policy Rules" title + "New Rule" button (supervisor only) + filter bar
- **Filters:** Scope (All/Global/Department), Department dropdown, Status (All/Draft/Active/Deprecated), Type (All/Threshold/Required Field/Semantic Policy/District Check/Date Window), Enabled toggle
- **Rules list** — card-based layout, each card shows:
  - **Left column:**
    - Rule name (bold)
    - Description/policy statement (truncated to 2 lines, expandable)
    - For semantic rules: "AI-Evaluated" badge with sparkle icon
    - For deterministic rules: field name + operator + threshold displayed as readable formula
  - **Right column:**
    - Scope badge: Global (blue) or Department (purple with dept name)
    - Severity badge: Error (red) / Warning (amber) / Info (blue)
    - Status badge: Draft (gray) / Active (green) / Deprecated (red strikethrough)
    - Enable/disable toggle switch (supervisor only)
    - Three-dot menu: Edit, Activate/Deprecate, View Audit Log, Delete (supervisor only)
  - **Bottom row** (subtle stats): "Triggered X times · Last triggered Y ago · Z% resolved"
- **"New Rule" modal** — stepped form:
  - Step 1: Choose rule type (cards with icons and descriptions for each type)
  - Step 2: Configure rule (dynamic form based on type):
    - **Semantic Policy:** Large text area for policy statement + severity + scope + doc types. Helper text: "Write your policy in plain English. The AI will evaluate each document against this statement and cite evidence from the source."
    - **Threshold:** Field dropdown + operator dropdown + value input + message template
    - **Required Field:** Field dropdown + message template
    - **District Check:** Auto-configured (checks scope_summary against Richmond districts)
    - **Date Window:** Date field dropdown + days input + message template
  - Step 3: Scope & targeting — global vs department (with dept dropdown), doc type multi-select
  - Step 4: Review & create — summary of the rule, "Create as Draft" and "Create & Activate" buttons
- **Edit modal:** Same form pre-populated with existing values. Cannot change `rule_type` after creation.

**Tab 2: Compliance Overview**
- **Department compliance cards** — one card per department showing:
  - Department name
  - Total documents count
  - Policy violations (error count), warnings count
  - "Compliance score" = (docs with 0 policy violations) / (total docs) as percentage with color coding (green >90%, amber 70-90%, red <70%)
- **Top triggered rules** — bar chart (Recharts) showing the 10 most-triggered rules by violation count
- **Severity breakdown** — donut chart of all policy validation results by severity
- **Recent violations** — table of the 10 most recent policy rule violations with document link, rule name, and severity
- Data source: aggregate query against `validation_results` joined with `validation_rule_configs` via `policy_rule_id`

**Tab 3: Audit Trail**
- **Chronological log** of all rule changes across all rules
- Each entry shows: timestamp, actor name, action (created/updated/toggled/activated/deprecated/deleted), rule name, diff summary (e.g., "severity: warning → error")
- Filter by: actor, action type, date range
- Data source: `GET /api/v1/validation-rules/audit-log?limit=50&offset=0`

**API endpoints needed for this page:**
- `GET /api/v1/validation-rules` (existing from S2)
- `GET /api/v1/validation-rules/compliance-summary` — department-level aggregates
- `GET /api/v1/validation-rules/audit-log` — global audit log (all rules)
- Mutations from S2 (create, update, toggle, activate, deprecate, delete)

**TanStack Query hooks:**
- `useValidationRules(filters)` — GET with filters
- `useCreateRule()` — POST mutation, invalidates rules query
- `useUpdateRule()` — PATCH mutation
- `useToggleRule()` — POST toggle mutation (optimistic update on the switch)
- `useActivateRule()` / `useDeprecateRule()` — POST lifecycle mutations
- `useDeleteRule()` — DELETE mutation with confirmation dialog
- `useComplianceSummary()` — GET compliance aggregates (30s polling like document list)
- `useRuleAuditLog(ruleId?)` — GET audit history (per-rule or global)

**Files:** `governance/page.tsx` (new), `layout.tsx` (update sidebar), `types.ts` (add types)

**Effort:** 3 hours

**Acceptance Criteria:**
- [ ] Governance page renders at `/dashboard/governance` with 3 tabs
- [ ] **Policy Rules tab:** Rules list loads with all filters working
- [ ] **Policy Rules tab:** Semantic policy rules show "AI-Evaluated" badge
- [ ] **Policy Rules tab:** Toggle switch enables/disables rules immediately (optimistic UI)
- [ ] **Policy Rules tab:** New Rule modal has stepped form with type-dependent fields
- [ ] **Policy Rules tab:** Semantic policy form has large text area with helper text
- [ ] **Policy Rules tab:** Rule lifecycle actions (activate, deprecate) work with confirmation
- [ ] **Policy Rules tab:** Analysts see rules in read-only mode (no edit/toggle/create)
- [ ] **Compliance Overview tab:** Department compliance cards show scores with color coding
- [ ] **Compliance Overview tab:** Top triggered rules chart renders with real data
- [ ] **Audit Trail tab:** Chronological log shows all rule changes with diffs
- [ ] Sidebar shows "Governance" with Shield icon instead of "Settings"
- [ ] `npx tsc --noEmit` passes
- [ ] `npm run build` succeeds

---

### S6: Policy Rule Results in Document Detail

**As an** analyst reviewing a document,
**I want** to see which policy rules triggered, the AI's reasoning and evidence citations, and which department the rule belongs to,
**so that** I understand both the system's automated checks and my department's specific governance requirements.

**Problem:** The current validation display doesn't distinguish between hardcoded system checks and configurable policy rules. Semantic rule results would appear with no context about the AI's reasoning or the evidence it found in the document.

**Implementation:**

**Backend — result format:**
- Semantic rule results store `rule_code = f"POLICY: {rule.name}"` (distinguishable from system rules which use ALL_CAPS codes like `MISSING_AMOUNT`)
- `ai_evidence` stored as newline-separated quotes
- `ai_confidence` stored as float 0.0-1.0

**Frontend — document detail page updates:**
- Split validation section into two collapsible groups:
  1. **"System Checks"** — existing hardcoded rules (rule_code is ALL_CAPS)
  2. **"Policy Rules"** — custom rules (rule_code starts with "POLICY:")
- Each group has its own error/warning/info badge counts
- Policy rule cards include additional information:
  - "AI-Evaluated" badge (for semantic rules, when `ai_confidence` is present)
  - AI confidence indicator (color-coded: green >0.85, amber 0.7-0.85, red <0.7)
  - **Evidence section** — expandable "View Evidence" that shows the quoted passages from the document, each in a blockquote with quotation mark styling
  - Department badge if the rule is department-scoped
  - Link to the rule in the GRC dashboard (using `policy_rule_id`)
- Resolve button works the same for both groups

**Files:** `engine.py` (rule_code format), `documents/[id]/page.tsx` (display), `types.ts` (update ValidationResult type)

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Validation section splits into "System Checks" and "Policy Rules" groups
- [ ] Each group has independent error/warning/info counts
- [ ] Semantic policy results show "AI-Evaluated" badge with confidence indicator
- [ ] "View Evidence" expands to show quoted passages from the source document
- [ ] Department-scoped rules show department badge
- [ ] Link to rule in GRC dashboard works
- [ ] Resolving policy rule validations works identically to system check validations
- [ ] Documents with no policy rule results don't show the "Policy Rules" section
- [ ] `npx tsc --noEmit` passes

---

### S7: Compliance Summary API Endpoint

**As a** GRC dashboard rendering compliance metrics,
**I want** an API endpoint that aggregates policy rule results by department,
**so that** the Compliance Overview tab has data to display.

**Problem:** No endpoint exists to aggregate validation results by department or rule. The frontend would need to load all documents and compute stats client-side, which doesn't scale.

**Implementation:**
- Add `GET /api/v1/validation-rules/compliance-summary` to `router.py`
- Returns:
  ```json
  {
    "departments": [
      {
        "department": "Public Works",
        "total_documents": 45,
        "documents_with_violations": 12,
        "compliance_score": 0.73,
        "error_count": 8,
        "warning_count": 15,
        "info_count": 3
      }
    ],
    "top_triggered_rules": [
      {
        "rule_id": "uuid",
        "rule_name": "MBE/WBE participation",
        "trigger_count": 23,
        "resolved_count": 18,
        "severity": "warning"
      }
    ],
    "recent_violations": [
      {
        "document_id": "uuid",
        "document_filename": "Contract_25000012048.pdf",
        "rule_name": "Insurance adequacy",
        "severity": "error",
        "message": "...",
        "triggered_at": "2026-03-28T14:30:00Z"
      }
    ]
  }
  ```
- SQL: Join `validation_results` (where `policy_rule_id IS NOT NULL`) with `documents` and `extracted_fields` (for `primary_department`)
- Group by department for compliance cards
- Aggregate by rule_code for top triggered
- Order by created_at desc for recent violations

- Add `GET /api/v1/validation-rules/audit-log` — global audit log with pagination
  - Optional filters: `?actor=X&action=created|updated|toggled&from_date=X&to_date=X`
  - Returns list of `ValidationRuleAuditLogSchema` ordered by `changed_at` desc

**Files:** `router.py`, `openapi.yaml`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Compliance summary returns per-department stats with compliance scores
- [ ] Top triggered rules returns the 10 most-triggered policy rules
- [ ] Recent violations returns the 10 most recent policy violations with document references
- [ ] Global audit log returns paginated, filterable change history
- [ ] Empty state (no policy rule results) returns valid empty arrays
- [ ] OpenAPI spec updated
- [ ] All existing backend tests pass

---

## Sprint Stories — NICE-TO-HAVE

### S8: Rule Preview — Test Against Existing Documents

**As a** supervisor creating a new policy rule,
**I want** to preview how many existing documents would trigger the rule before activating it,
**so that** I can tune the rule's sensitivity and avoid flooding analysts with false positives.

**Problem:** Without preview, a supervisor creates a rule, activates it, and discovers it flags 80% of documents — too late to avoid noise.

**Implementation:**
- Add `POST /api/v1/validation-rules/preview` endpoint
- Accepts a rule configuration (same as create payload) + `limit` (default 20)
- Runs the rule against the N most recent extracted documents:
  - For deterministic rules: evaluate directly
  - For semantic rules: batch-evaluate against Azure OpenAI (with `max_completion_tokens=400` for preview)
- Returns: `{ "total_tested": 20, "would_trigger": 7, "sample_results": [...] }`
- Frontend: "Preview" button on the New Rule modal (Step 4) that shows results before creating

**Files:** `router.py`, `governance/page.tsx`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] Preview endpoint evaluates a rule against recent documents without creating ValidationResults
- [ ] Returns count of documents that would trigger + sample results with reasoning
- [ ] Semantic rules are evaluated via Azure OpenAI in preview mode
- [ ] Preview doesn't persist any data (read-only operation)
- [ ] Frontend shows preview results in the New Rule modal

---

### S9: Rule Import/Export for Cross-Department Sharing

**As a** supervisor sharing proven rules with another department,
**I want** to export rules as JSON and import them,
**so that** departments can adopt best practices without re-creating rules from scratch.

**Implementation:**
- `GET /api/v1/validation-rules/export` — returns all active rules as JSON array
- `POST /api/v1/validation-rules/import` — accepts JSON array, creates as draft rules (skip name-duplicates), creates audit log entries
- Frontend: Export (download JSON) and Import (file upload + preview) buttons on Governance page

**Files:** `router.py`, `governance/page.tsx`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Export returns valid JSON with all rule fields
- [ ] Import creates rules as `draft` status (must be manually activated)
- [ ] Name-duplicate rules are skipped with a warning
- [ ] Audit log records import events
- [ ] Round-trip (export → import) produces functionally identical rules

---

### S10: Retrospective Scan via Azure AI Search

**As a** supervisor who just created a new policy rule,
**I want** to scan all existing documents for potential violations using semantic search,
**so that** I can identify non-compliant documents that were processed before the rule existed.

**Problem:** New rules only apply to future uploads. Existing documents are never re-evaluated unless manually reprocessed one by one.

**Implementation:**
- Build Azure AI Search index from existing OCR text + extracted fields (leverages the configured but unimplemented AI Search credentials)
- `POST /api/v1/validation-rules/{id}/retroactive-scan` — indexes relevant documents, runs semantic evaluation, creates ValidationResults for violations found
- Shows progress in GRC dashboard as a background operation

**Files:** `search/` (new directory), `router.py`, `governance/page.tsx`

**Effort:** 3 hours

**Acceptance Criteria:**
- [ ] Azure AI Search index is populated with document content
- [ ] Retroactive scan finds violations in previously-processed documents
- [ ] Results are persisted as ValidationResults linked to the policy rule
- [ ] Progress is visible in the GRC dashboard

---

### S11: Rule Templates Library

**As a** supervisor who isn't sure what policies to create,
**I want** a library of pre-built rule templates based on common procurement governance patterns,
**so that** I can adopt best practices with one click instead of writing policies from scratch.

**Implementation:**
- Hardcoded template library in `procurement/backend/app/validation/templates.py`
- Categories: Financial Controls, Insurance & Bonding, Compliance & Equity, Contract Terms, Geographic
- `GET /api/v1/validation-rules/templates` — returns template library
- Frontend: "Browse Templates" button on New Rule modal, searchable/filterable template gallery
- "Use Template" pre-fills the rule creation form

**Files:** `validation/templates.py` (new), `router.py`, `governance/page.tsx`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Template library has 15+ templates across 5 categories
- [ ] Templates include realistic policy statements for semantic rules
- [ ] "Use Template" pre-fills the creation form correctly
- [ ] Templates are searchable by name and category

---

## QA Verification Plan

After implementing any story, verify:

1. **Backend tests pass:** `cd procurement/backend && .venv/bin/python -m pytest -v --tb=short`
2. **Frontend type-check:** `cd procurement/frontend && npx tsc --noEmit`
3. **Frontend build:** `cd procurement/frontend && npm run build`
4. **Semantic policy smoke test:**
   - Create a semantic_policy rule: "All contracts must include a termination for convenience clause"
   - Upload a contract that lacks this clause
   - Verify the policy rule triggers with AI reasoning and evidence quotes
   - Verify `ai_confidence` is present and reasonable (>0.7)
   - Upload a contract that HAS a termination clause → verify COMPLIES (no violation)
5. **Deterministic rule smoke test:**
   - Create a threshold rule: total_amount > 100000, severity=warning
   - Upload a contract with amount $150K → rule triggers
   - Toggle the rule off → reprocess → rule no longer appears
6. **Department scoping test:**
   - Create a department-scoped semantic_policy rule for "Public Works"
   - Upload a Public Works contract → rule fires
   - Upload a Finance contract → rule does NOT fire
7. **Lifecycle test:**
   - Create a rule (starts as draft) → verify it does NOT fire on new documents
   - Activate the rule → verify it fires
   - Deprecate the rule → verify it stops firing
   - Check audit log → all 3 state changes recorded
8. **GRC dashboard test:**
   - Verify compliance cards show department-level stats
   - Verify top triggered rules chart has data
   - Verify audit trail shows recent changes

---

## Implementation Priority Order

```
S1 Data model + schemas        ████████ 45m        ← Foundation — everything depends on this
S2 CRUD API + audit logging    ██████████████ 1.5h  ← Backend complete, testable via curl
S3 Semantic evaluation engine  ████████████████████ 2.5h ← The core innovation — AI evaluates policy rules
S4 Seed default rules          ██████ 30m          ← Demo-ready out of the box
S7 Compliance summary API      ████████████ 1h     ← Data layer for GRC dashboard
S6 Document detail display     ████████████ 1h     ← Users see AI reasoning + evidence
S5 GRC dashboard               ████████████████████████████ 3h ← Full governance interface
─────────────────────────────────────────────
Total MUST-HAVE:               ~10.25 hours

S8  Rule preview               ██████████████ 1.5h
S9  Import/export              ████████ 45m
S11 Templates library          ████████████ 1h
S10 Retroactive scan (AI Search) ████████████████████████ 3h
─────────────────────────────────────────────
Total NICE-TO-HAVE:            ~6.25 hours
```

---

## Architecture Decision Records

### ADR-1: Semantic policy evaluation via Azure OpenAI, not regex/keyword matching
**Decision:** Replace `regex_match` and `keyword_check` rule types with a single `semantic_policy` type that sends natural-language policy statements to Azure OpenAI for evaluation.
**Why:** City policies are written in natural language. Regex requires technical decomposition that loses nuance and misses semantically equivalent phrasing. The LLM already understands procurement concepts (it's the same model doing extraction) and can reason about compliance across document sections. A policy like "subcontractor flow-down clauses" is impossible to express as a regex but trivial for the LLM.
**Trade-off:** Each document processing adds one Azure OpenAI API call (~800 tokens output). Mitigated by batching all semantic rules into a single call and skipping entirely when no semantic rules are active.

### ADR-2: Batched single-call evaluation, not per-rule calls
**Decision:** All applicable semantic rules are evaluated in one API call per document, not one call per rule.
**Why:** 10 rules x 50 documents = 500 API calls with per-rule approach. Batched = 50 calls. Same quality, 10x fewer API calls, 10x lower cost and latency. The strict JSON schema ensures structured output even with multiple rules.

### ADR-3: Hardcoded rules remain as non-negotiable baseline
**Decision:** The 13 existing hardcoded rules in `engine.py` stay unchanged. Custom rules layer on top.
**Why:** Hardcoded rules are battle-tested and cover universal procurement risks. Custom rules are *additive* — departments can raise the bar but not lower it below the baseline. This prevents a supervisor from accidentally disabling critical checks.

### ADR-4: Rule lifecycle (draft → active → deprecated) instead of simple enable/disable
**Decision:** Rules have both a `status` lifecycle and an `enabled` toggle. `status` controls whether the rule participates in evaluation at all. `enabled` is a quick toggle within active rules.
**Why:** GRC requires governance over the rules themselves. A new policy should be reviewable (draft) before it starts generating compliance findings. Deprecation preserves history — you can see what rules were active when a document was evaluated. Simple delete would lose that audit trail.

### ADR-5: Department matching via existing AI-extracted fields
**Decision:** Use `primary_department` and `department_tags` from `ExtractedFields` to match department-scoped rules.
**Why:** The AI extractor already populates these fields. No new extraction logic needed. If a document's department isn't extracted, department-scoped rules simply don't fire (safe default).

### ADR-6: GRC dashboard as a first-class dashboard section, not settings
**Decision:** Governance lives at `/dashboard/governance` with its own sidebar entry (Shield icon), three tabs, and dedicated compliance analytics — not under Settings.
**Why:** Governance is an operational function, not a configuration task. City officials think in terms of GRC (Governance, Risk & Compliance). Placing it alongside the document portfolio elevates it to equal importance. The Compliance Overview tab with department scores and triggered-rule charts gives supervisors a control-plane view they can't get anywhere else in the system.

### ADR-7: Richmond districts as hardcoded reference list
**Decision:** Maintain Richmond's 9 districts and ~25 neighborhoods as a Python list, not a DB table.
**Why:** These change extremely rarely (district boundaries are set by city charter). A DB table adds complexity for data that's essentially static. Can always promote to DB later if needed.

### ADR-8: Azure AI Search for retrospective scan only (nice-to-have), not real-time evaluation
**Decision:** Use Azure OpenAI for real-time per-document evaluation. Reserve Azure AI Search for the retrospective scan feature (S10, nice-to-have).
**Why:** AI Search excels at *retrieval* (finding relevant documents from a corpus) but not *evaluation* (determining if a specific document complies with a specific policy). Real-time evaluation needs structured verdicts with confidence scores and evidence — that's an LLM task. AI Search becomes valuable when you need to scan 1,000+ existing documents for a new rule — it can pre-filter candidates before sending them to the LLM.
