# cross_report_synthesis

Purpose: Synthesize findings from multiple research reports into a coherent answer while preserving source traceability and acknowledging uncertainty.

## When To Use
- A user asks a question that spans multiple reports or sections
- A team needs a summary of findings across a problem domain
- An agent needs to answer: "What does the research say about X across all relevant reports?"
- A user asks for a synthesis of risks, opportunities, or data sources

## Inputs
- User question or synthesis goal
- List of relevant report files (from `research_corpus_navigation` skill)
- Access to the source `.md` files

## Outputs
- Synthesized answer with per-claim source citations
- Tensions or contradictions noted explicitly
- Confidence level per claim (confirmed, likely, uncertain)
- List of reports read vs. reports not read
- Identified gaps where synthesis is incomplete

## Process

### Step 1 — Load Navigation Context

Before synthesizing, confirm you have run `research_corpus_navigation` or equivalent to identify which files are relevant. Do not synthesize from random file selections.

### Step 2 — Read Source Files Fully

For each file in the reading list:
1. Read the full `.md` file (not just summaries or frontmatter)
2. Note specific claims, data points, named entities, and source citations
3. Note the confidence level of each claim: does the report cite a primary source, or is it a secondary synthesis?

Do NOT synthesize from index.json summaries alone. Summaries are navigation aids, not authoritative content.

### Step 3 — Build a Claim Map

For each substantive claim you plan to include:

```
Claim: [statement]
Source: [filename, section heading if helpful]
Confidence: confirmed | likely | uncertain
Primary source: [URL or citation if available in the report]
Conflicts with: [other report + how it conflicts, if applicable]
```

### Step 4 — Identify Tensions and Gaps

Before writing the synthesis, explicitly check:
- Do any reports contradict each other? (If so, note both positions and their sources)
- Are there claims that appear in one report but are absent from others where you would expect them?
- Are there questions that the reports together still do not answer?

Flag gaps with: `[Gap: no report in this corpus addresses X]`

### Step 5 — Write the Synthesis

Structure:
1. **Scope**: which files were read, which were not
2. **Main findings**: 3–7 bullet points with inline citations
3. **Tensions**: any conflicting information and its sources
4. **Gaps**: what the corpus does not cover
5. **Confidence summary**: overall confidence in the synthesis

### Citation Format

Use inline citations:
- `(per research/A1_problem_landscape_service_navigation.md)`
- `(per evidence_log.md, entry E-008)`
- `[Unverified: not found in files read]`
- `[Uncertain: mentioned in summary but not verified in source]`

Never blend claims from different sources into a single uncited sentence.

### Step 6 — State What Was NOT Read

Always end the synthesis with:

```
Files read for this synthesis:
  - research/[FILE].md
  - research/[FILE].md

Files not read (possibly relevant):
  - research/[FILE].md — reason it may contain relevant information
```

This allows the user or a future agent to know the synthesis is incomplete if additional files exist.

## Anti-Patterns to Avoid

- **Never** synthesize from index.json summaries alone
- **Never** blend claims from different reports without attribution
- **Never** omit tensions or contradictions to make the answer cleaner
- **Never** claim the synthesis is complete if relevant unread files exist
- **Never** invent figures or statistics not present in the source files
- **Never** conflate the 2014–2015 historical 311 dataset with current RVA311 operations

## Example Output Structure

```
**Synthesis: 311 Data Availability for a Service Navigation Tool**

Files read: A1, C1, D1, D4, 02_data/source_inventory.csv
Files not read (possibly relevant): D5 (data quality), H4 (no-API build strategies)

**Main Findings**
1. RVA311 launched June 2018 replacing SeeClickFix; it has no public API (per C1; cited in evidence_log.md E-002).
2. Historical Socrata dataset (vgg4-hjn8) contains 43,273 SeeClickFix records from Jan 2014–Aug 2015 only (per D1; cited in evidence_log.md E-001).
3. rva.gov uses Drupal 8+ on Acquia with 40+ department slugs; Drupal Search API with Facets is accessible (per A1, C2).
4. In 2025, more than half of all RVA311 interactions were resolved by phone without a ticket (per A1; primary source: Richmond press release [cited in A1]).

**Tensions**
- A1 describes navigation as the primary problem; C4 notes service gaps where no department owns the request — synthesis requires reading both before recommending a single fix.

**Gaps**
- [Gap: no report read directly addresses the 311 category taxonomy as it exists in the current AvePoint system — H4 likely addresses this]

**Confidence: Moderate** — main findings confirmed; D5 and H4 not read, so data quality and no-API build strategies are incomplete.
```
