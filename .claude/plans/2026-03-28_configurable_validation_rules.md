# ContractIQ — Configurable Validation Rules

> Sprint plan for enabling city officials and admins to define, scope, and toggle validation rules applied during the AI extraction pipeline.

---

## Context

ContractIQ currently has **13 hardcoded validation rules** in `engine.py` that run identically on every document. This works for a universal baseline, but Richmond's departments have fundamentally different risk profiles:

- **Public Works** needs bond requirements on *all* contracts (not just >$100K)
- **Finance** flags anything over $500K for extra scrutiny
- **Parks & Recreation** must verify neighborhood references match real Richmond districts
- **Procurement** wants to enforce MBE/WBE participation on contracts above a threshold

Today, none of this is configurable. A supervisor who wants stricter rules has no lever to pull — they're stuck with the same checks as every other department.

### Why now?

The hackathon judges are city officials. Showing that the system adapts to *their* department's rules — not just generic ones — demonstrates real-world value. This also addresses the demo risk where a judge asks "but what about *our* specific requirements?" and we have nothing to show.

### Design principles

1. **Additive, not replacement** — hardcoded rules stay as the baseline; custom rules layer on top
2. **No new infrastructure** — rules live in the existing Azure SQL database, no Redis/Celery
3. **Department matching uses existing fields** — `primary_department` and `department_tags` from ExtractedFields (already populated by the AI extractor)
4. **Supervisor-level management** — supervisors create/toggle rules; analysts see the results

---

## Data Model

### New table: `validation_rule_configs`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | PK |
| `name` | VARCHAR(100) | Human-readable name, e.g. "Require bonds for Public Works" |
| `description` | TEXT | Explanation shown in UI |
| `rule_type` | VARCHAR(30) | `threshold`, `required_field`, `keyword_check`, `district_check`, `date_window`, `regex_match` |
| `scope` | VARCHAR(20) | `global` or `department` |
| `department` | VARCHAR(100), nullable | NULL for global rules; department name for scoped rules |
| `severity` | VARCHAR(20) | `error`, `warning`, `info` |
| `field_name` | VARCHAR(100), nullable | Which extracted field this rule checks |
| `operator` | VARCHAR(20), nullable | `gt`, `lt`, `gte`, `lte`, `eq`, `neq`, `contains`, `not_contains`, `is_empty`, `is_not_empty` |
| `threshold_value` | VARCHAR(255), nullable | Comparison value (stored as string, cast at runtime) |
| `keywords` | JSON, nullable | List of keywords for keyword_check rules |
| `message_template` | TEXT | Template with `{field}`, `{value}`, `{threshold}` placeholders |
| `suggestion` | TEXT, nullable | Recommended action |
| `enabled` | BOOLEAN | Default TRUE |
| `applies_to_doc_types` | JSON, nullable | NULL = all; or list like `["contract", "purchase_order"]` |
| `created_by` | VARCHAR(100) | Who created the rule |
| `created_at` | DATETIME | Auto |
| `updated_at` | DATETIME | Auto |

### Richmond districts reference data

Hardcoded list in a new `procurement/backend/app/validation/districts.py`:
```
RICHMOND_DISTRICTS = [
    "1st District", "2nd District", ..., "9th District"
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

## Sprint Stories — MUST-HAVE

### S1: ValidationRuleConfig Model & Migration

**As a** system storing custom validation rules,
**I want** a database table that persists rule configurations,
**so that** rules survive server restarts and can be managed via API.

**Problem:** All validation logic is hardcoded. There's no database representation of configurable rules.

**Implementation:**
- Add `ValidationRuleConfig` SQLAlchemy model to `procurement/backend/app/models/document.py`
- Fields as specified in the data model above
- `applies_to_doc_types` and `keywords` as JSON columns (same pattern as `department_tags`)
- Table created automatically via `init_db()` (existing pattern — no Alembic needed for hackathon)
- Add corresponding Pydantic schemas to `procurement/backend/app/schemas/document.py`:
  - `ValidationRuleConfigCreate` (input)
  - `ValidationRuleConfigUpdate` (partial update)
  - `ValidationRuleConfigSchema` (response)

**Files:** `models/document.py`, `schemas/document.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] `ValidationRuleConfig` model exists with all columns from data model
- [ ] Pydantic schemas for create, update, and response exist
- [ ] Table is created on server startup via `init_db()`
- [ ] All existing backend tests pass

---

### S2: CRUD API for Validation Rules

**As a** supervisor managing validation rules,
**I want** API endpoints to create, list, update, and toggle rules,
**so that** I can configure validation behavior without touching code.

**Problem:** No API exists to manage validation rules. Supervisors have no way to add, edit, or disable rules.

**Implementation:**
- Add endpoints to `procurement/backend/app/api/router.py`:
  - `GET /api/v1/validation-rules` — list all rules (optional `?scope=global|department&department=X&enabled=true|false`)
  - `POST /api/v1/validation-rules` — create a rule (supervisor only)
  - `PATCH /api/v1/validation-rules/{id}` — update a rule (supervisor only)
  - `DELETE /api/v1/validation-rules/{id}` — delete a rule (supervisor only)
  - `POST /api/v1/validation-rules/{id}/toggle` — quick enable/disable (supervisor only)
- Role check: if `created_by` header role is not "supervisor", return 403
- Validate `rule_type` is one of the supported types
- Validate `operator` is valid for the given `rule_type`

**Files:** `router.py`, `openapi.yaml`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] All five CRUD endpoints work and return correct schemas
- [ ] Supervisor can create, update, toggle, and delete rules
- [ ] List endpoint supports filtering by scope, department, and enabled status
- [ ] Invalid rule_type or operator returns 422 with descriptive error
- [ ] OpenAPI spec updated with new endpoints
- [ ] All existing backend tests pass

---

### S3: Custom Rule Evaluation Engine

**As a** validation engine processing a document,
**I want** to evaluate all enabled custom rules in addition to hardcoded rules,
**so that** department-specific and global custom rules are applied automatically.

**Problem:** `validate_document()` only runs hardcoded rules. Custom rules in the DB are never evaluated.

**Implementation:**
- Add `_evaluate_custom_rules(fields: dict, custom_rules: list[ValidationRuleConfig]) -> list[dict]` to `engine.py`
- For each enabled rule, check scope:
  - `global`: always applies
  - `department`: only if document's `primary_department` or `department_tags` match rule's `department`
- Check `applies_to_doc_types`: skip if doc type not in the list (NULL = apply to all)
- Evaluate by `rule_type`:
  - **`threshold`**: Compare `fields[field_name]` against `threshold_value` using `operator` (cast numeric fields to float)
  - **`required_field`**: Check if `fields[field_name]` is present and non-empty
  - **`keyword_check`**: Check if any keyword in `keywords` list appears in `fields[field_name]` (case-insensitive)
  - **`district_check`**: Validate that location/neighborhood references in the document match known Richmond districts/neighborhoods
  - **`date_window`**: Check if a date field falls within N days of today (e.g., "expiration within 60 days")
  - **`regex_match`**: Apply regex pattern from `threshold_value` against `fields[field_name]`
- Render `message_template` with `{field}`, `{value}`, `{threshold}` substitution
- Return results in same dict format as existing rules: `rule_code = f"CUSTOM_{rule.id[:8].upper()}"`, severity, message, field_name, suggestion

- Update `validate_document()` to:
  1. Accept optional `custom_rules` parameter
  2. Call `_evaluate_custom_rules()` after hardcoded rules
  3. Combine results

- Update `pipeline.py` to:
  1. Query enabled `ValidationRuleConfig` records from DB before calling `validate_document()`
  2. Pass them to the function

**Files:** `engine.py`, `pipeline.py`, `validation/districts.py` (new)

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] `threshold` rule: "total_amount > 500000" triggers warning on a $600K contract
- [ ] `required_field` rule: "bond_required is_not_empty" triggers on contract missing bond info
- [ ] `keyword_check` rule: keywords ["asbestos", "hazmat"] in scope_summary triggers warning
- [ ] `district_check` rule: validates neighborhood references against Richmond list
- [ ] `date_window` rule: "expiration within 60 days" triggers warning
- [ ] Department-scoped rules only fire for matching departments
- [ ] Global rules fire for all documents
- [ ] Disabled rules are skipped
- [ ] `applies_to_doc_types` filtering works (e.g., contracts only)
- [ ] Custom rule results appear alongside hardcoded results in ValidationResult table
- [ ] All existing backend tests pass

---

### S4: Seed Default Custom Rules

**As a** demo presenter showing the system to city judges,
**I want** pre-loaded rules that demonstrate department-specific validation,
**so that** the feature has immediate "wow factor" without manual setup.

**Problem:** An empty rules table during the demo defeats the purpose of the feature.

**Implementation:**
- Add `_seed_default_rules(session)` function to `main.py`, called during lifespan after `init_db()`
- Only seed if `validation_rule_configs` table is empty (idempotent)
- Seed these rules:

| Name | Type | Scope | Department | Severity |
|------|------|-------|------------|----------|
| High-value contract alert | threshold | global | — | warning |
| Require bond for Public Works | required_field | department | Public Works | error |
| MBE/WBE required above $50K | threshold + required | global | — | warning |
| Verify Richmond district | district_check | global | — | warning |
| Hazardous materials keyword flag | keyword_check | global | — | error |
| Contract duration > 5 years | date_window | global | — | warning |
| Missing insurance for large contracts | threshold + required | department | Finance | error |

**Files:** `main.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] On first startup with empty table, 7 default rules are seeded
- [ ] On subsequent startups, no duplicates are created
- [ ] Each seeded rule has a descriptive name, message_template, and suggestion
- [ ] Rules are immediately visible via `GET /api/v1/validation-rules`
- [ ] All existing backend tests pass

---

### S5: Validation Rules Admin UI

**As a** supervisor configuring validation rules,
**I want** a settings page where I can view, create, toggle, and edit rules,
**so that** I can manage validation without using the API directly.

**Problem:** The Settings link in the sidebar is a dead placeholder. Supervisors have no UI for rule management.

**Implementation:**
- Create `procurement/frontend/src/app/dashboard/settings/page.tsx` — validation rules management page
- Update sidebar link in `layout.tsx` to point to `/dashboard/settings`
- Only accessible to supervisors (redirect analysts to dashboard)
- Page sections:
  1. **Header**: "Validation Rules" with "Add Rule" button
  2. **Filter bar**: Scope (All/Global/Department), Department dropdown, Status (All/Enabled/Disabled)
  3. **Rules table/cards**: Each rule shows:
     - Name + description
     - Scope badge (Global = blue, Department = purple with dept name)
     - Severity badge (same colors as document detail page)
     - Rule type tag
     - Enable/disable toggle switch
     - Edit and Delete buttons
  4. **Add/Edit modal**: Form with fields for all rule properties
     - Rule type selector (changes which fields are visible)
     - Scope toggle (global vs department, with department dropdown)
     - Severity selector
     - Field name dropdown (populated from ExtractedFields)
     - Operator dropdown (filtered by rule type)
     - Threshold value input
     - Keywords input (comma-separated, for keyword_check)
     - Doc type multi-select (contract, purchase_order, etc.)
     - Message template with placeholder help text
     - Suggestion text

- TanStack Query hooks:
  - `useValidationRules()` — GET with filters
  - `useCreateRule()` — POST mutation
  - `useUpdateRule()` — PATCH mutation
  - `useToggleRule()` — POST toggle mutation
  - `useDeleteRule()` — DELETE mutation with confirmation dialog

**Files:** `settings/page.tsx` (new), `layout.tsx` (update sidebar), `types.ts` (add types)

**Effort:** 2 hours

**Acceptance Criteria:**
- [ ] Settings page renders at `/dashboard/settings`
- [ ] Supervisors see full CRUD interface; analysts are redirected
- [ ] Rules list loads from API with working filters
- [ ] Toggle switch enables/disables rules via API (immediate, no save button)
- [ ] Add Rule modal creates a rule with all required fields
- [ ] Edit updates existing rule
- [ ] Delete has confirmation dialog
- [ ] Scope badge distinguishes global vs department rules
- [ ] `npx tsc --noEmit` passes
- [ ] `npm run build` succeeds

---

### S6: Custom Validation Results in Document Detail

**As an** analyst reviewing a document,
**I want** to see which custom rules triggered and which department they belong to,
**so that** I understand department-specific requirements for this contract.

**Problem:** The current validation display doesn't distinguish between hardcoded and custom rules. Custom rule results would appear with cryptic `CUSTOM_A1B2C3D4` codes.

**Implementation:**
- Store the custom rule's `name` in the ValidationResult `rule_code` field (prefixed: `CUSTOM: {name}`)
- In document detail page validation section, add visual distinction:
  - Custom rules show a small "Custom" tag next to the severity badge
  - Department-scoped rules show the department name as a secondary badge
  - Rule description shown as tooltip or expandable detail
- Group validations: "System Checks" (hardcoded) and "Policy Rules" (custom) with collapsible sections

**Files:** `engine.py` (rule_code format), `documents/[id]/page.tsx` (display)

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Custom rule results display with "Custom" tag
- [ ] Department-scoped results show department badge
- [ ] Validation section has "System Checks" and "Policy Rules" groups
- [ ] Resolving custom rule validations works same as hardcoded ones
- [ ] `npx tsc --noEmit` passes

---

## Sprint Stories — NICE-TO-HAVE

### S7: Rule Import/Export

**As a** supervisor sharing rules between departments,
**I want** to export rules as JSON and import them into another instance,
**so that** departments can share best practices.

**Implementation:**
- `GET /api/v1/validation-rules/export` — returns all rules as JSON array
- `POST /api/v1/validation-rules/import` — accepts JSON array, creates rules (skip duplicates by name)
- Frontend: Export and Import buttons on the settings page

**Files:** `router.py`, `settings/page.tsx`

**Effort:** 45 minutes

**Acceptance Criteria:**
- [ ] Export returns valid JSON with all rule fields
- [ ] Import creates rules and skips name-duplicates
- [ ] Round-trip (export → import) produces identical rules

---

### S8: Rule Effectiveness Dashboard

**As a** supervisor evaluating validation rules,
**I want** to see how often each rule triggers and how often it's resolved vs acted on,
**so that** I can tune or retire noisy rules.

**Implementation:**
- `GET /api/v1/validation-rules/stats` — returns per-rule hit count, resolved count, last triggered
- Add stats cards to the settings page showing rule effectiveness
- Highlight "noisy" rules (>80% resolved without action = probably too sensitive)

**Files:** `router.py`, `settings/page.tsx`

**Effort:** 1 hour

**Acceptance Criteria:**
- [ ] Stats endpoint returns trigger_count, resolved_count, last_triggered per rule
- [ ] Settings page shows stats inline with each rule
- [ ] Rules with >80% resolve rate are visually flagged as "noisy"

---

### S9: Rule Versioning & Audit Trail

**As a** compliance officer reviewing rule changes,
**I want** a history of who changed which rules and when,
**so that** we have an audit trail for policy changes.

**Implementation:**
- Add `ValidationRuleHistory` model (rule_id, changed_by, changed_at, change_type, old_values JSON, new_values JSON)
- Record on every create, update, toggle, delete
- Display in settings page as expandable history per rule

**Files:** `models/document.py`, `router.py`, `settings/page.tsx`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] Every rule change creates a history record
- [ ] History shows who, when, and what changed
- [ ] History is viewable in the settings UI

---

## QA Verification Plan

After implementing any story, verify:

1. **Backend tests pass:** `cd procurement/backend && .venv/bin/python -m pytest -v --tb=short`
2. **Frontend type-check:** `cd procurement/frontend && npx tsc --noEmit`
3. **Frontend build:** `cd procurement/frontend && npm run build`
4. **Custom rule smoke test:**
   - Create a threshold rule: total_amount > 100000, severity=warning
   - Upload a contract with amount $150K
   - Verify the custom rule appears in validation results on document detail
   - Toggle the rule off, reprocess, verify it no longer appears
5. **Department scoping test:**
   - Create a department-scoped rule for "Public Works"
   - Upload a Public Works contract → rule fires
   - Upload a Finance contract → rule does NOT fire
6. **District check test:**
   - Create a district_check rule
   - Upload a contract mentioning "Church Hill" → passes
   - Upload a contract mentioning "Fakeville" → triggers warning

---

## Implementation Priority Order

```
S1 Model & schemas         ██████ 30m          <- Foundation, everything depends on this
S2 CRUD API                ████████████ 1h     <- Backend complete, testable via curl
S3 Evaluation engine       ██████████████████ 1.5h <- Rules actually run during pipeline
S4 Seed default rules      ██████ 30m          <- Demo-ready out of the box
S6 Detail page display     ████████ 45m        <- Users see custom rule results
S5 Admin UI                ████████████████████████ 2h <- Full management interface
─────────────────────────────────────────────
Total MUST-HAVE:           ~6.25 hours

S7  Import/export          ████████ 45m
S8  Effectiveness stats    ████████████ 1h
S9  Versioning & audit     ██████████████████ 1.5h
─────────────────────────────────────────────
Total NICE-TO-HAVE:        ~3.25 hours
```

---

## Architecture Decision Records

### ADR-1: Custom rules in DB, not config files
**Decision:** Store rules in `validation_rule_configs` table, not YAML/JSON config files.
**Why:** Rules need to be created/modified at runtime by supervisors via UI. File-based config would require server restarts and code deploys.

### ADR-2: Hardcoded rules remain as baseline
**Decision:** The 13 existing hardcoded rules in `engine.py` stay unchanged. Custom rules layer on top.
**Why:** Hardcoded rules are battle-tested and cover universal procurement risks. Custom rules are *additive* — departments can raise the bar but not lower it below the baseline.

### ADR-3: Department matching via existing AI-extracted fields
**Decision:** Use `primary_department` and `department_tags` from `ExtractedFields` to match department-scoped rules.
**Why:** The AI extractor already populates these fields. No new extraction logic needed. If a document's department isn't extracted, department-scoped rules simply don't fire (safe default).

### ADR-4: Richmond districts as hardcoded reference list
**Decision:** Maintain Richmond's 9 districts and ~25 neighborhoods as a Python list, not a DB table.
**Why:** These change extremely rarely (district boundaries are set by city charter). A DB table adds complexity for data that's essentially static. Can always promote to DB later if needed.

### ADR-5: Rule types are extensible via enum, not plugin architecture
**Decision:** Support 6 rule types (`threshold`, `required_field`, `keyword_check`, `district_check`, `date_window`, `regex_match`) via if/elif dispatch.
**Why:** Hackathon scope. A plugin architecture is overkill for 6 types. The if/elif block in `_evaluate_custom_rules()` is easy to extend later.
