# ContractIQ — Intelligence Backfill Plan

> Strategy for populating department routing, compliance, insurance, and procurement fields on all existing records.

---

## Problem Statement

We added 17 new intelligence columns (S15–S18) to `ExtractedFields`, but all existing records have NULLs in these fields because they were processed before the schema was expanded. The dashboard shows "--" for every row.

**Two distinct data populations need different strategies:**

| Population | Count | Has OCR Text? | Has `issuing_department`? | Has `raw_extraction`? | Strategy |
|---|---|---|---|---|---|
| **Socrata CSV imports** | ~1,362 | No | Yes (from CSV `Agency/Department`) | Yes (full CSV row) | Deterministic mapping — no AI needed |
| **Uploaded PDFs** | 4–10 | Yes | Maybe | Yes | Re-extract via AI pipeline, or update demo cache |

---

## Data Analysis — Socrata

The Socrata CSV contains two fields that map directly to our new schema:

### `Agency/Department` → `primary_department` + `department_tags`

| CSV Value | Count | Maps To |
|---|---|---|
| Public Utilities | 399 | `PUBLIC_UTILITIES` |
| Public Works | 371 | `PUBLIC_WORKS` |
| City Wide | 123 | `PROCUREMENT` (cross-department) |
| Information Technology | 101 | `INFORMATION_TECHNOLOGY` |
| Human Resources | 44 | `HUMAN_RESOURCES` |
| Parks, Recreation and Community Facilities | 42 | `PARKS_RECREATION` |
| Police Department | 41 | `PUBLIC_SAFETY` |
| Finance | 38 | `FINANCE` |
| Planning & Development Review | 34 | `PLANNING_DEVELOPMENT` |
| Emergency Communication | 28 | `PUBLIC_SAFETY` |
| Fire and Emergency Services | 26 | `PUBLIC_SAFETY` |
| City Attorney | 14 | `FINANCE` (legal/fiscal) |
| (blank) | 10 | `OTHER` |
| Sheriff's Office | 8 | `PUBLIC_SAFETY` |
| Procurement Services | 8 | `PROCUREMENT` |
| Not Listed | 8 | `OTHER` |
| DGS | 8 | `PUBLIC_WORKS` (General Services) |
| City Council | 6 | `OTHER` |
| Library | 6 | `COMMUNITY_DEVELOPMENT` |
| Economic Development | 5 | `COMMUNITY_DEVELOPMENT` |

### `Procurement Type` → `procurement_method`

| CSV Value | Count | Maps To |
|---|---|---|
| Invitation to Bid | 539 | `COMPETITIVE_BID` |
| Cooperative Agreement | 240 | `COOPERATIVE_PURCHASE` |
| Request for Proposal | 196 | `RFP` |
| Agency Request | 89 | `SOLE_SOURCE` |
| Small Purchase | 31 | `COMPETITIVE_BID` |
| Exempt Purchase | 12 | `SOLE_SOURCE` |

### `Type of Solicitation` → additional context

| CSV Value | Count | Intelligence |
|---|---|---|
| Non Professional Services | 364 | `contract_type` refinement |
| Construction - Capital/Non-Capital | 109 | Likely needs bonds, insurance |
| Supplies, Materials, Parts | 89 | Lower compliance burden |
| Professional Services | 74 | Likely needs E&O insurance |
| Equipment - Non Technology | 59 | Standard procurement |
| Construction - Term | 40 | Needs bonds + insurance |
| Commodity | 27 | Standard procurement |
| Equipment - Technology | 14 | IT-related |

### Heuristic Compliance Rules (no AI needed)

From the contract analysis and City of Richmond procurement standards:

1. **Construction contracts** (Type of Solicitation contains "Construction") → `bond_required: true`, `insurance_required: true`, `workers_comp_required: true`, `compliance_flags: ["ENVIRONMENTAL"]`
2. **Contracts > $100K via Competitive Bid** → likely `mbe_wbe_required: true`
3. **Professional Services** → `insurance_professional_liability_min` likely required
4. **All City contracts** → `compliance_flags: ["DRUG_FREE_WORKPLACE"]` (standard clause)
5. **Cooperative Purchase** → set `cooperative_contract_ref` from description if present
6. **Police/Fire/Emergency** → `PUBLIC_SAFETY` department tag

---

## Implementation Plan

### S25: Socrata Backfill — Deterministic Department & Procurement Mapping

**Strategy:** Pure Python mapping — no AI calls, no cost, instant execution.

**Implementation:**
- Add a backfill endpoint `POST /api/v1/ingest/backfill-intelligence`
- Query all documents where `source = "socrata"` and `primary_department IS NULL`
- For each record, read `raw_extraction` (contains original CSV row) and `issuing_department`
- Apply deterministic mapping rules (tables above)
- Batch update in groups of 200

**Mapping functions:**
```python
def _map_department(issuing_dept: str) -> tuple[str, list[str]]:
    """Map Socrata Agency/Department to primary_department + tags."""

def _map_procurement_method(procurement_type: str) -> str:
    """Map Socrata Procurement Type to procurement_method enum."""

def _infer_compliance(solicitation_type: str, amount: float, dept: str) -> dict:
    """Infer compliance flags from solicitation type and amount."""
```

**Fields populated:**
- `primary_department` — from `Agency/Department` mapping
- `department_tags` — from department + cross-reference with description keywords
- `department_confidence` — 1.0 (authoritative source data)
- `procurement_method` — from `Procurement Type` mapping
- `mbe_wbe_required` — heuristic: true for contracts > $100K via competitive bid/RFP
- `compliance_flags` — heuristic: construction → bonds/insurance/environmental
- `bond_required` — true for construction solicitation types
- `insurance_required` — true for construction + professional services
- `workers_comp_required` — true for construction
- `prequalification_required` — false (Socrata doesn't track this)

**Files:** New `procurement/backend/app/api/backfill.py`, register in `main.py`

**Effort:** 1.5 hours

**Acceptance Criteria:**
- [ ] `POST /api/v1/ingest/backfill-intelligence` populates all ~1,362 Socrata records
- [ ] "Public Works" department maps to `PUBLIC_WORKS`
- [ ] "Invitation to Bid" maps to `COMPETITIVE_BID`
- [ ] Construction contracts get `bond_required: true` and compliance flags
- [ ] Endpoint is idempotent (running twice doesn't duplicate or overwrite)
- [ ] Response reports count of updated records
- [ ] All backend tests pass

---

### S26: Demo Cache Update — Add Intelligence Fields to Cached Extractions

**Strategy:** Manually add the new fields to the 4 demo cache entries in `fixtures/demo_cache.py`. These are the contracts that get pre-populated when running in PLACEHOLDER mode.

**Fields to add per cached contract:**

**Contract 25000012048 (Insight/Flock — Goods & Services):**
```python
"department_tags": ["PUBLIC_SAFETY", "INFORMATION_TECHNOLOGY"],
"primary_department": "PUBLIC_SAFETY",
"department_confidence": 0.95,
"mbe_wbe_required": False,
"federal_funding": False,
"compliance_flags": ["DRUG_FREE_WORKPLACE"],
"insurance_general_liability_min": None,
"insurance_auto_liability_min": None,
"insurance_professional_liability_min": None,
"workers_comp_required": None,
"performance_bond_amount": None,
"payment_bond_amount": None,
"liquidated_damages_rate": None,
"procurement_method": "COOPERATIVE_PURCHASE",
"cooperative_contract_ref": "OMNIA Partners / Cobb County #23-6692-03",
"prequalification_required": False,
```

**Contract 24000006048 (Insight/Flock — Cooperative):**
```python
"department_tags": ["PUBLIC_SAFETY", "INFORMATION_TECHNOLOGY"],
"primary_department": "PUBLIC_SAFETY",
"department_confidence": 0.95,
"mbe_wbe_required": False,
"federal_funding": False,
"compliance_flags": ["DRUG_FREE_WORKPLACE"],
"procurement_method": "COOPERATIVE_PURCHASE",
"cooperative_contract_ref": "OMNIA Partners / Cobb County #23-6692-03",
"prequalification_required": False,
```

**Contract 25000005766 (Sidewalk — Construction):**
```python
"department_tags": ["PUBLIC_WORKS", "COMMUNITY_DEVELOPMENT"],
"primary_department": "PUBLIC_WORKS",
"department_confidence": 0.98,
"mbe_wbe_required": True,
"mbe_wbe_details": "MBE/WBE participation and affidavit requirements per City policy",
"federal_funding": False,
"compliance_flags": ["MBE_WBE", "ADA", "DRUG_FREE_WORKPLACE", "VDOT_STANDARDS", "ENVIRONMENTAL"],
"insurance_general_liability_min": 2000000,
"insurance_auto_liability_min": 1000000,
"insurance_professional_liability_min": 1000000,
"workers_comp_required": True,
"performance_bond_amount": 676000,
"payment_bond_amount": 676000,
"liquidated_damages_rate": "$600 per calendar day",
"procurement_method": "COMPETITIVE_BID",
"cooperative_contract_ref": None,
"prequalification_required": False,
```

**Contract 22000011432 (Public Works — Construction):**
```python
"department_tags": ["PUBLIC_WORKS", "PUBLIC_UTILITIES", "TRANSPORTATION"],
"primary_department": "PUBLIC_WORKS",
"department_confidence": 0.95,
"mbe_wbe_required": True,
"federal_funding": False,
"compliance_flags": ["MBE_WBE", "DRUG_FREE_WORKPLACE", "VDOT_STANDARDS", "ENVIRONMENTAL"],
"insurance_general_liability_min": 2000000,
"insurance_auto_liability_min": 1000000,
"insurance_professional_liability_min": 1000000,
"workers_comp_required": True,
"performance_bond_amount": None,
"payment_bond_amount": None,
"liquidated_damages_rate": "$600 per calendar day",
"procurement_method": "COMPETITIVE_BID",
"cooperative_contract_ref": None,
"prequalification_required": False,
```

**Files:** `fixtures/demo_cache.py`

**Effort:** 30 minutes

**Acceptance Criteria:**
- [ ] All 4 demo cache entries include the 17 new fields
- [ ] Re-seeding in PLACEHOLDER mode populates intelligence columns
- [ ] Dashboard shows department badges and compliance chips for demo contracts
- [ ] All backend tests pass

---

### S27: Socrata Ingest Enhancement — Populate Intelligence on New Imports

**Strategy:** Update the Socrata ingest endpoint so that all *future* imports automatically populate the intelligence fields using the same deterministic mapping from S25.

**Implementation:**
- Import the mapping functions from `backfill.py` into `ingest.py`
- In the `_parse_csv_rows` loop, call the mapping functions to add intelligence fields to each row dict
- Pass them through to `ExtractedFields()` constructor

**Files:** `ingest.py`

**Effort:** 20 minutes

**Acceptance Criteria:**
- [ ] Re-running `POST /api/v1/ingest/socrata` on a fresh DB populates intelligence fields
- [ ] New Socrata records show department badges in the list view
- [ ] Existing dedup logic still works (no duplicate records)

---

## Implementation Priority

```
S26 Demo cache update        ██████ 30m   ← Immediate demo visibility
S25 Socrata backfill         ██████████████ 1.5h ← 1,362 records populated
S27 Ingest enhancement       ████ 20m     ← Future-proofs new imports
──────────────────────────────────────────
Total:                       ~2.25 hours
```

---

## Expected Outcome

After backfill, the dashboard list view will show:

| Filename | Department | Vendor | Amount | Compliance | Procurement |
|---|---|---|---|---|---|
| 15000014256-ITRON_INC.csv | **Public Utilities** | ITRON INC | $5,000,000 | -- | Co-op |
| 15000014906-Bug_Busters... | **Public Works** | Bug Busters... | $550,000 | Bond | Competitive Bid |
| 16000003460-AXON_ENTERP... | **Public Safety** | AXON ENTERPRISE | $3,399,896 | -- | Sole Source |
| Contract 25000005766.pdf | **Public Works** | Simons Contracting | $676,000 | MBE Bond | Competitive Bid |

Instead of the current all-dashes view.
