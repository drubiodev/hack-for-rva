<div align="center">

# A Thriving City Hall — Decision Funnel

Richmond Civic Hackathon • March 27–29, 2026

[![Pillar](https://img.shields.io/badge/Pillar-A_Thriving_City_Hall-4c68d7)](#)
[![Stage](https://img.shields.io/badge/Stage-Decision_Funnel-00a38f)](#)
[![Focus](https://img.shields.io/badge/Focus-From_Idea_%E2%86%92_MVP-ff7a59)](#)

</div>

This is a guided decision environment for teams working on the A Thriving City Hall pillar. It's designed to help you quickly choose a credible, source‑linked, weekend‑buildable MVP—and avoid fantasy software.

Journey stages: Land → Orient → Choose → Research → Compare MVPs → Lock Scope → Build → Validate → Demo → Hand‑off

Three questions to answer fast: 1) What problem are we actually solving? 2) Can we credibly demo by Sunday? 3) What should we refuse to build?

---

## The Challenge

**→ Full detail in [`CHALLENGE.md`](CHALLENGE.md).** Read it before anything else — it defines the two problems, the top blue sky vision, data constraints, and exactly how judges will score your solution.

### Problem 1: Helping Residents Find the Right City Service or Next Step — 27/32 — Strong

> How might we use technology to help Richmond residents quickly determine the right next step when interacting with City services so that issues are routed correctly the first time?

Build toward: Resident service navigation tool (plain language → right department) · 311 category guide or chatbot · City website plain-language search helper · Staff-facing triage tool

⚠ Post-2018 RVA311 data does not exist in any public API. The AvePoint platform has no API. The historical Socrata dataset (2014–2015 only) is not representative of current request types.

---

### Problem 2: Helping City Staff Review Procurement Risks and Opportunities — 22/32 — Needs work

> How might we use technology to help Richmond staff identify valid, compliant, and cost-effective purchasing contracts across City, state, and federal sources with less manual review?

Build toward: Procurement contract risk dashboard · Contract PDF key-term extractor · Multi-source contract explorer · Staff decision-support tool

⚠ The City Contracts Socrata API has a known bug — use the CSV download instead. VITA contract portal has no API. Sample procurement PDFs must be sourced before building.

---

### Top Blue Sky: Making Fiscal Responsibility More Visible — 21/27 — Strong

> How might we use technology to make Richmond's fiscal decisions, contract awards, and budget spending more visible and understandable to residents and oversight bodies?

Strong data foundation: City Contracts Socrata, SAM.gov, eVA, VITA are all publicly available. A transparency explorer is directly buildable. Label everything as exploratory — not official City financial reporting.

---

### Pillar Award Rubric

| Category | Weight | Dominant question |
|----------|--------|-------------------|
| **Impact** | **5** | Does this directly address one of the two problems above? |
| User Value | 4 | Is there a specific real user? Does the prototype improve their experience? |
| Feasibility | 3 | Could this be piloted by a City department or 311 team within a year? |
| Innovation | 3 | Fresh thinking on service navigation or procurement transparency? |
| Execution | 3 | Does a working demo exist? Is the flow coherent? |
| Equity | 3 | Does it reach residents who struggle most with City service navigation? |

Full rubric with scoring anchors and judge instructions: [`../RUBRIC.md`](../RUBRIC.md)

---

## Table of Contents

0. [The Challenge](#the-challenge)
1. Quick Start
2. Repo Map
3. Guardrails
4. Decision Phases
   - Phase 0: Landing & Framing
   - Phase 1: Rapid Orientation
   - Phase 2: Problem Selection
   - Phase 3: Research Spin‑Up
   - Phase 4: Opportunity Framing
   - Phase 5: Scope Lock
   - Phases 6–9: Build → Validate → Demo
5. Verification Workflow
6. Hackbot Helper
7. Appendix: Pillar Context & Rubric

---

## Quick Start

Do these first 15–30 minutes to get moving:

1) Read: `CHALLENGE.md` — the two problems, top blue sky, and rubric (start here, not QUICKSTART.md)
2) Read: `QUICKSTART.md`
2) Skim: `00_core/00_pillar_overview.md` and `01_problem_space/02_targeted_problem_statements.md`
3) Capture a 5‑bullet "Working Direction" using `99_templates/working_direction_note.md`
4) Decide your path:
   - Path A — already have a rough problem: jump to Phase 2 and Phase 4
   - Path B — need help choosing: start at Phase 1 and proceed in order

---

## Repo Map

- Research hub: `research_notes.md`
- Evidence tracker: `evidence_log.md`
- Data index: `02_data/00_index.md`
- Source inventory (CSV): `02_data/source_inventory.csv`
- Research corpus: `research/` (51 deep research reports, see `research/INDEX.md`)
- Artifacts: `03_artifacts/`
  - Journeys: `03_artifacts/user_journeys.md`
  - Prototype recommendations: `03_artifacts/prototype_recommendations.md`
  - Benchmark scan: `03_artifacts/benchmark_scan.md`
  - Continuation plan: `03_artifacts/continuation_plan.md`
  - City Hall tech inventory: `03_artifacts/city_hall_tech_inventory.md`
- Build guides: `04_build_guides/`
- Prompts + runners: `05_prompts/`
- Templates: `99_templates/`

### Navigation files

| File | Purpose |
|------|---------|
| `CORPUS_GUIDE.md` | Canonical guide for humans and AI agents navigating the research corpus |
| `manifest.json` | Machine-readable index of all significant files in this repository |
| `research/index.json` | Machine-readable index of all 51 research reports (summaries + key_terms) |
| `research/INDEX.md` | Human-readable table of contents for the research directory |
| `MAINTENANCE.md` | How to add, update, and synchronize reports and metadata |

---

## Guardrails

- Pick one user, one workflow, and one credible data/doc base.
- Avoid eligibility/legal determinations and policy/integration dependencies.
- Always cite official sources. Log every claim in `evidence_log.md`.
- Keep AI constrained to explanation, retrieval, comparison, and guidance.
- Never claim post-2018 RVA311 data is accessible via API — it is not.

---

## Decision Phases

<details open>
<summary><strong>Phase 0 — Landing & Framing</strong></summary>

Goal: understand what this repo is and how to use it without "exploring" for two hours.

What this pillar is about:
- Government service delivery, resident access to City services, staff efficiency, and procurement integrity under A Thriving City Hall.

Success patterns:
- Source‑linked, narrow scope, credible demo, explicit limits.

Anti‑patterns:
- Platform claims; eligibility/legal decisions; policy/integration dependencies; private data needs; tools requiring post-2018 311 API access.

Admin quick links:
- Research hub: `research_notes.md`
- Evidence tracker: `evidence_log.md`
- Source inventory (CSV): `02_data/source_inventory.csv`
- Artifacts: see Repo Map above

Call to action: choose Path A or Path B.

</details>

<details open>
<summary><strong>Phase 1 — Rapid Orientation (20–30 min)</strong></summary>

Read just enough to build a shared mental model:
- `QUICKSTART.md`
- `00_core/00_pillar_overview.md`
- `00_core/01_map_alignment.md`
- `01_problem_space/02_targeted_problem_statements.md`

Filter for:
- user groups; pain points; what the City actually cares about
- problems that are software‑shaped vs policy‑shaped

Team checkpoint — Working Direction (use `99_templates/working_direction_note.md`):

```
## Working Direction
- Pillar: A Thriving City Hall
- Candidate problem:
- Likely user:
- Why it matters:
- Why it seems weekend-buildable:
- Biggest uncertainty:
```

</details>

<details>
<summary><strong>Phase 2 — Problem Selection (30–45 min)</strong></summary>

Files:
- `01_problem_space/01_bluesky_problem_statements.md`
- `01_problem_space/02_targeted_problem_statements.md`
- `00_core/04_solution_patterns.md`
- `05_prompts/01_problem_selection_prompt.md`

Decision rule — choose only if the problem has:
- a real user and understandable workflow
- a plausible public data/document base
- a demoable artifact by Sunday

Output: Decision Memo (`99_templates/decision_memo.md`)

```
## Chosen Problem
## User
## Why this one
## Why not the others
## Risks
```

</details>

<details>
<summary><strong>Phase 3 — Research Spin‑Up (60–90 min)</strong></summary>

Goal: gather just enough evidence to avoid fantasy software.

Use the runner to execute targeted prompts and capture findings:
- Perplexity runner: `05_prompts/perplexity_runner/` (see its README)
- Data index: `02_data/00_index.md`

Evidence Log structure (log in `evidence_log.md`):

```
## Evidence Log
### Confirmed
### Likely but unverified
### Missing
### Useful datasets
### Useful source documents
### Prior art
### Risks
```

Tip: parse URLs from API metadata; don't ask for URLs in prompt text.

</details>

<details>
<summary><strong>Phase 4 — Opportunity Framing (45–60 min)</strong></summary>

Compare at least two MVP shapes before choosing.

Files:
- `04_build_guides/01_mvp_shapes.md`
- `04_build_guides/02_recommended_architectures.md`
- `05_prompts/06_risk_review_prompt.md`

Output:

```
## MVP Options
1. …
2. …
3. …

## Recommended MVP
## Why
## What we are explicitly not building
```

</details>

<details>
<summary><strong>Phase 5 — Scope Lock (45–60 min)</strong></summary>

Pin down must‑haves, mockables, data, AI role, limits, and demo path.

Files:
- `99_templates/project_one_pager_template.md`

Key sentence:

> By Sunday, we will show a prototype that helps [user] do [specific thing] using [specific data/docs], without pretending to do [dangerous overclaim].

</details>

<details>
<summary><strong>Phases 6–9 — Build → Validate → Demo</strong></summary>

Build:
- Break work into FE/BE/data/content; assign source verification and demo owner.
- Keep AI constrained to explanation, retrieval, comparison, and guidance.

Validate:
- Use risk review prompts and red flags; check source links and clarity.

Demo:
- Follow `04_build_guides/05_demo_advice.md`.

</details>

---

## Verification Workflow

1) Add official URLs and dates in `evidence_log.md`; flip status to Verified.
2) Mirror verified sources into `02_data/source_inventory.csv` with access mode and key fields.
3) After verification, promote findings into the Executive Brief inside `research_notes.md`.

---

## Hackbot Helper

You can use Hackbot to reconstruct context, run research, and shape an MVP.

- Boot prompt: `HACKBOT_BOOT_PROMPT.md`
- Team profile (recommended): `99_templates/team_profile_template.md`

**Team skills:** repo_memory, problem_scoping, research_runner, dataset_mapper, opportunity_mapper, mvp_designer, risk_review, demo_coach, repo_librarian, continuity_planner

**Research corpus skills:** research_corpus_navigation, cross_report_synthesis, evidence_grounded_answering, report_update_protocol

Hackbot resources:

| Resource | File |
|----------|------|
| Agent specification | `AGENTS.md` |
| Boot prompt | `HACKBOT_BOOT_PROMPT.md` |
| Corpus guide | `CORPUS_GUIDE.md` |
| Full file manifest | `manifest.json` |
| Research index | `research/index.json` |
| All skills | `skills/**/SKILL.md` |

Notes:
- Hackbot never invents government programs or legal eligibility. It cites official sources and encourages verification.
- For best results, create a team profile so Hackbot can map tasks to roles and follow your communication preferences.

---

## Appendix: Pillar Context & Rubric

<details>
<summary>Open context from the Pillar Committee session (March 13, 2026)</summary>

Prepared by: Pillar Committee et al. (March 13, 2026)

Pillar Committee & Working Session
- Session: March 13, 2026, 12:30 PM – 2:30 PM
- Pillar: 1 — A Thriving City Hall

Rubric Score Summary
| Statement                        | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | Total | Band       |
|----------------------------------|----|----|----|----|----|----|----|----|-------|------------|
| Resident Service Navigation      |    |    |    |    |    |    |    |    | 27    | Strong     |
| Procurement Risk Review          |    |    |    |    |    |    |    |    | 22    | Needs work |

Dimension key: D1 Clarity | D2 Scope | D3 Data readiness | D4 Champion | D5 Population & impact | D6 Operating environment | D7 Success criteria | D8 Accessibility

Quick‑kill flags:
- Both targeted statements lack an explicit continuation pathway.
- Resident Service Navigation has stronger implicit champion support (Pete Briel, Director of 311) but commitment is not formalized.
- Procurement Risk Review lacks a named departmental champion.
- Sample procurement PDFs are not pre-staged.
- 311 routing decision logic is undocumented.

Targeted Statement 1: Helping Residents Find the Right City Service or Next Step (Score 27/32 — Strong)
- Problem, context, constraints, success, data constraints are in `01_problem_space/02_targeted_problem_statements.md`.
- Key champion contact: Pete Briel, Director of 311 (not yet formally committed).

Targeted Statement 2: Helping City Staff Review Procurement Risks and Opportunities (Score 22/32 — Needs work)
- Problem, context, constraints, success, data sources are in `01_problem_space/02_targeted_problem_statements.md`.
- Lacks named champion; sample PDFs not staged; procurement workflow undocumented.

Blue Sky Statements
- See `01_problem_space/01_bluesky_problem_statements.md`.

Prioritized Actions Before March 27, 2026
1) Name departmental champion (Pete Briel for Resident Service Navigation)
2) Pre-stage sample procurement PDFs (5–10 representative contracts)
3) Document the 311 routing decision logic
4) Specify output types for each problem statement
5) Verify rva.gov sitemap and structured data availability

</details>
