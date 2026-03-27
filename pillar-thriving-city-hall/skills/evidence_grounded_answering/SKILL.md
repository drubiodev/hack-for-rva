# evidence_grounded_answering

Purpose: Answer user questions using only content actually present in this repository corpus, with explicit grounding and uncertainty marking.

## When To Use
- Any time a factual claim about Richmond City Hall systems, programs, or data is being made
- When a user asks: "Does X exist?" "Is Y available?" "What does the City do about Z?"
- When an agent is about to state something it cannot directly verify from files it has read
- Before asserting that a dataset, system, service, or policy exists
- Before stating any specific figure (request volume, update cadence, field count, etc.)

## Inputs
- User question
- Files read in current context
- Optional: `evidence_log.md` for verified claims

## Outputs
- Answer grounded in specific file content
- Inline citations for each substantive claim
- Explicit uncertainty markers for unverified statements
- "Not found" statements when information is absent

## Process

### Step 1 — Establish What Has Been Read

Before answering, state (internally or explicitly) which files have been read. Only make claims from those files. Do not interpolate from general knowledge.

### Step 2 — Classify Each Claim

For every substantive claim in your answer, classify it:

| Status | Meaning | Marker |
|--------|---------|--------|
| `Confirmed` | Present in a source file AND has an entry in `evidence_log.md` | No marker needed; cite source |
| `Stated in corpus` | Present in a research file but not independently verified | `(per [filename])` |
| `Uncertain` | Implied or summarized but not directly stated in a file read | `[Uncertain: implied by X but not stated directly]` |
| `Not found` | Not present in any file read | `[Not found in files read]` |
| `Requires reading` | Likely in a specific file that has not been read | `[Requires reading: filename]` |

### Step 3 — Check the Evidence Log

For claims about:
- Specific dataset IDs, URLs, and their capabilities
- 311 system architecture or API availability
- Processing timelines or SLAs
- rva.gov structure or platform details
- City Contracts dataset schema and access

Cross-check `evidence_log.md`. If the claim has an `E-` entry, you can cite it. Most entries in this log are currently `Unverified` — do not treat them as confirmed unless the log row shows a verified source URL and date.

### Step 4 — Formulate the Answer

Structure:
1. Direct answer to the question
2. Supporting evidence with citations
3. Explicit uncertainty statements
4. What is NOT covered (to set expectations)

### Step 5 — Apply the Anti-Fabrication Check

Before finalizing the answer, run this check:

- Does every named government system actually appear in a file I have read?
- Does every dataset I mentioned actually appear in D section files or `02_data/`?
- Does every URL I mentioned appear in `evidence_log.md` or a research file?
- Am I inventing specificity (exact request counts, exact dates, specific field names) not present in the source?
- Am I treating the 2014–2015 historical 311 data as if it represents current RVA311 operations? (It does not.)

If any check fails → remove or mark the claim as `[Unverified]`.

### Step 6 — State Scope Limits

At the end of the answer, state:
- What files were used to answer this question
- What topics the answer does NOT cover because relevant files were not read

## Required Language

When information is absent, use:
- "This repository does not contain that information."
- "I cannot verify that from the files I have read in this session."
- "That would require reading [specific file] which I have not yet loaded."
- "[Unverified]: this appears in a summary but I have not read the source file."

Do NOT use:
- "Likely..." (without a citation)
- "Generally..." (as a hedge for an ungrounded claim)
- "It is common for cities to..." (implies external knowledge not in corpus)
- "I believe..." (implies opinion substituting for evidence)
- "RVA311 currently has..." (unless citing a specific research file with a dated source)

## Example

**Question:** "Is there a public API for Richmond's 311 data?"

**Grounded answer:**

No. RVA311 launched in June 2018 on AvePoint Citizen Services (Dynamics 365) and has no public API (per `research/C1_services_311_landscape.md`; noted in `evidence_log.md` entry E-002, currently unverified). The historical SeeClickFix dataset (Socrata ID vgg4-hjn8) covers only January 2014–August 2015 and does not represent current operations (per `research/D1_data_311_historical.md`; noted in evidence_log.md E-001, currently unverified).

For teams building a 311 navigation tool, `research/H4_mvp_data_constraints.md` covers strategies for building without API access. `[Requires reading: H4 if you need those strategies]`

*Files read for this answer: C1, D1, evidence_log.md*
*Not covered: D4 (rva.gov content access), H2 (service navigation MVP scope), H4 (no-API build strategies)*

## Anti-Patterns

- Never state a City system feature exists without a source file citation
- Never quote a statistic (request volume, percentage, processing time) without a source
- Never say "RVA311 supports X" based only on index.json summaries
- Never blend confirmed and uncertain claims in the same sentence without differentiation
- Never treat the 2014–2015 SeeClickFix Socrata data as equivalent to current 311 data
- Never claim the 311 system has a public API — evidence_log.md E-002 states it does not
