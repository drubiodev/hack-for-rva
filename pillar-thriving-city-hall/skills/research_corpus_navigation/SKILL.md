# research_corpus_navigation

Purpose: Map a user question to the correct section and specific research reports in the A Thriving City Hall corpus before attempting to answer.

## When To Use
- A user asks any research question about Richmond's government operations, service delivery, or procurement
- A user asks about a specific problem domain (resident service navigation, 311, rva.gov, procurement contracts)
- A user asks what reports to read
- An agent needs to determine which files are relevant before answering

## Inputs
- User question or information need (natural language)

## Outputs
- Identified section(s) from the research corpus
- List of specific files to read (in recommended order)
- Brief explanation of why each file is relevant
- Any files that must be read before answering (prerequisites)

## Process

### Step 1 — Load Navigation Artifacts

Before looking at any research file, load:
1. `research/index.json` — scan all summaries and key_terms
2. If the corpus is unfamiliar: read `CORPUS_GUIDE.md` first

Do NOT skip this step and dive directly into research files.

### Step 2 — Classify the Question

Determine which category the user question falls into:

| Question Category | Relevant Sections |
|------------------|------------------|
| "What problems exist in this space?" | Section A (A1–A5) |
| "Who are the users or stakeholders?" | Section B (B1–B5) |
| "What services or systems exist?" | Section C (C1–C5) |
| "What public data is available?" | Section D (D1–D5), `02_data/` |
| "What has been built elsewhere?" | Section E (E1–E5) |
| "What should we build?" | Section F (F1–F5) |
| "What could go wrong?" | Section G (G1–G5) |
| "Is this feasible for a weekend?" | Section H (H1–H5) |
| "How should we demo this?" | Section I (I1–I5) |
| "What is the overall picture?" | `research_notes.md`, `00_pillar_summary_context.md` |
| "What datasets or APIs are mentioned?" | D1, D2, D3, `02_data/source_inventory.csv` |
| "Resident service navigation specific" | A1, A5, B1, C1, C2, D4, F2, H2, H4 |
| "Procurement contract review specific" | A2, B3, C3, D2, D3, F3, H3 |

### Step 3 — Search `research/index.json`

Scan the `key_terms` and `summary` fields for matches to the user's question. Identify:
- High-confidence matches (3+ matching key_terms)
- Medium-confidence matches (1–2 matching key_terms)
- Files worth reading despite no term match (based on section relevance)

### Step 4 — Build a Reading List

Order files by:
1. Direct relevance to the question
2. Section order (earlier sections provide context for later ones)
3. Files mentioned in `CORPUS_GUIDE.md` recommended reading orders

Limit the initial reading list to 5 files maximum. If more are needed after reading, say so.

### Step 5 — Identify Prerequisites

Some questions require reading prerequisite files:
- Any question requiring context about Richmond City Hall → read `00_pillar_summary_context.md` first
- Any question about specific services or systems → read C1 before C2–C5
- Any question about data → read D1 (311) or D2 (contracts) before other D files
- Any question requiring problem framing → read A1 or A2 before F or H sections

Flag prerequisites explicitly.

### Step 6 — Output the Navigation Result

Return:
```
Relevant section(s): [X, Y]
Files to read (in order):
  1. research/[FILE].md — [one-sentence reason why]
  2. research/[FILE].md — [one-sentence reason why]
  3. ...

Prerequisites (read these first if not yet read):
  - research/[FILE].md — [reason]

Files to skip (and why):
  - [Section] — not relevant because [reason]
```

### Step 7 — Confirm Scope Boundaries

After delivering the reading list, state:
- What sections were NOT included and why (to confirm you didn't miss something)
- Whether cross-report synthesis will be needed
- Whether any answer requires verified facts from `evidence_log.md`

## Example

**Question:** "What data can we use to build a contract expiry dashboard?"

**Navigation result:**
```
Relevant sections: D (Data Inventory), A (Problem Landscape), F (Opportunities)

Files to read (in order):
  1. research/D2_data_contracts.md — primary source on City Contracts Socrata dataset (xqn7-jvv2)
  2. research/D3_data_federal_procurement.md — SAM.gov, eVA, USAspending data access details
  3. research/A2_problem_landscape_procurement_review.md — context on what data gaps create problems
  4. research/F3_opportunities_procurement.md — contract expiry dashboard opportunity framing
  5. 02_data/source_inventory.csv — verified data source list with access details

Prerequisites: none (D2 is the logical starting point)

Files to skip: B, C1, C2, E, G, H, I — not directly relevant to data availability question

Verified facts to check: evidence_log.md (E-008, E-009 cover City Contracts Socrata access and schema)
```
