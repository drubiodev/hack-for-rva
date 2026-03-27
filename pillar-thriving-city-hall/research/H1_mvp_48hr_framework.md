---
title: "48-Hour City Hall MVPs — What You Can Actually Ship, Safely"
pillar: thriving-city-hall
section: H
problem_statement: general
tags:
  - 48-hour-mvp
  - feasibility
  - City-Contracts
  - Socrata
  - PyMuPDF
  - time-budget
summary: "48-hour feasibility framework with specific technical guidance: City Contracts Socrata as primary data source, PyMuPDF for PDF extraction, JSON schema enforcement for LLM routing, and Friday/Saturday/Sunday time budget breakdown."
geography: Richmond, VA
source: parallel-ai-pro
status: raw
related_reports:
  - H2_mvp_service_navigation
  - H3_mvp_procurement
  - H5_mvp_scope_boundaries
  - F1_opportunities_ranked
---

# 48-Hour City Hall MVPs — What You Can Actually Ship, Safely

## Executive Summary

For a hackathon team with 17–21 effective build hours, success depends on ruthless prioritization and avoiding hidden technical traps. The most viable path to a compelling "A Thriving City Hall" demo relies on the City of Richmond's open Socrata datasets, specifically the City Contracts data, which is readily available and updated monthly [1]. Conversely, attempting to integrate the Payment Register will stall your team, as it is gated behind an SSO login [2]. 

When integrating advanced features, opt for zero-ops or low-dependency tools. For PDF extraction, PyMuPDF is significantly faster to set up than Unstructured, which requires heavy system dependencies like poppler and tesseract [3] [4]. For LLM routing, be aware that models like GPT-4o-mini can struggle with structured output reliability, occasionally missing keys or hallucinating values [5]. You must enforce strict JSON schemas and implement retry logic [6]. Ultimately, your team should aim to ship two core components flawlessly rather than five fragile ones.

## Context and Constraints

With only 17–21 effective build hours, your team must focus on a single, reliable demo path. 

### Team and Time Window Specifics
Your time budget is strictly limited: Friday evening allows 3–4 hours for setup and data access; Saturday provides 10–12 hours for the main build; and Sunday morning leaves 4–5 hours for finishing and demo prep. With a mixed team of 2–3 developers, 1 PM, and 1 UX designer, parallelizing work is essential.

### Demo-Narrative First Approach
Define a 90-second user story on Friday night. Every task must map directly to this narrative. If a feature does not actively improve the demo script, it should be cut until after the first dry run.

## Data Source Feasibility

Your data strategy must prioritize sources that require zero authentication and minimal cleaning.

### Richmond Procurement Datasets: City Contracts Ready; Payments Gated
The City of Richmond provides a robust City Contracts dataset covering open and closed contracts for the past 5 years, updated monthly [1]. This data includes agency names, contract numbers, dollar amounts, and supplier names, making it an ideal anchor for your MVP [1] [7]. However, the Payment Register dataset requires users to be logged in via SSO to access the page [2]. Anchor your build on City Contracts and treat Payments as out-of-scope.

### Content Search Scope on rva.gov: Manual Set Beats Broad Crawl
The rva.gov website is highly navigable, featuring clear links to 311, the Mayor's Office, and various departments [8]. However, building a broad crawler in 48 hours is risky. Instead, manually curate 50–100 relevant URLs tied to your demo narrative, scrape them to JSON, and index them using a client-side tool like Lunr.js.

### SAM.gov: Plan for Offline Sample
Live API calls to SAM.gov introduce significant risks regarding API key registration and rate limits. Plan to use static JSON examples for any SAM.gov data to avoid live dependencies during the demo.

| Component | Optimistic Hours | Likely Hours | Risk Hours | Key Takeaway |
| :--- | :--- | :--- | :--- | :--- |
| City Contracts (Socrata CSV) | 0.5 | 1.5 | 3.5 | Fast, reliable anchor data. |
| rva.gov page curation + scrape | 1.0 | 3.0 | 6.0 | Manual curation prevents crawl traps. |
| SAM.gov API (live) | 1.0 | 3.0 | 7.0 | High risk; use static JSON fallback (0.5h). |
| Decision tree (5–8 Qs) | 3.0 | 5.0 | 7.0 | Time is spent on authoring, not coding. |
| Search index (Lunr.js) | 1.0 | 2.5 | 3.0 | Client-side indexing is safest. |
| Search index (Typesense/Docker) | 2.0 | 4.0 | 5.0 | Server ops risk. |
| Frontend (HTML form/table) | 1.0 | 1.5 | 2.0 | Low risk, stable demo. |
| Frontend (React dashboard) | 3.0 | 5.0 | 6.0 | High polish, but time-heavy. |
| PyMuPDF PDF extract | 0.25 | 0.75 | 1.5 | Fast setup for text extraction. |
| Unstructured PDF extract | 1.0 | 2.0 | 3.0 | Heavy system dependencies. |
| LLM routing integration | 1.0 | 2.0 | 4.0 | Requires strict schema and retries. |

Time estimates show that relying on static data and simple frontends drastically reduces risk.

## 311 Router Scope

Building the routing engine is quick; finalizing the taxonomy is the actual bottleneck.

### Authoring and Validation Workflow
The PM and UX designer should draft 5–8 questions mapping to 15–20 categories aligned with visible 311 services. Define clear outputs for each leaf: category key, department, and contact/action link.

### Implementation Plan
Build a simple JSON-driven tree with a basic renderer that stores the user's path and result. The final output should be a recommendation card with links to relevant rva.gov department pages [8].

## Search Index Strategy

Deliver fast relevance with zero server operations to protect your Sunday morning.

### Tooling Comparison and Choice
Lunr.js provides a client-side, small index with instant deployment. Typesense or Meilisearch offer better ranking and typo-tolerance but require Docker or cloud server setups, which can derail a hackathon timeline.

### Crawl/Curate Approach
Curate your URLs manually. Write a simple script to extract the title, headings, and body text, and save this as a static JSON file to feed your index.

| Option | Setup | Index Size | Pros | Cons | Likely Hours |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Lunr.js | No server | Small, in-browser | Fast, simple deploy | Limited ranking | 2–3 |
| Typesense | Docker/Cloud | Medium | Typo-tolerance, facets | Server ops required | 3–5 |
| Meilisearch | Docker/Cloud | Medium | Great defaults | Server ops required | 3–5 |

Lunr.js is the optimal choice for a 48-hour window due to its zero-ops deployment.

## Frontend Path

Prioritize reliability over visual richness to ensure a functional demo.

| UI Choice | Use Case | Build Time | Risk | Demo Impact |
| :--- | :--- | :--- | :--- | :--- |
| Simple HTML form/table | Router + contracts list | 1–2h | Low | Clear, stable, fast |
| React dashboard | Analytics + filters | 4–6h | Medium | Slick, but consumes polish time |

Start with a simple HTML/Tailwind approach. Only upgrade to a React dashboard if a developer is completely idle on Saturday afternoon.

## LLM/NLP Integration

Add AI features only if they are strictly guardrailed and can be easily disabled.

### PDF Extraction Path
For PDF extraction, PyMuPDF is highly recommended as it can extract text in minutes using simple Python commands [4]. The Unstructured library, while powerful, requires system dependencies like `libmagic-dev`, `poppler-utils`, and `tesseract-ocr`, which can consume valuable hackathon hours [3].

### Structured Outputs Risk and Mitigation
When using LLMs for routing, be aware that models like GPT-4o-mini can be unreliable, sometimes missing keys or generating inaccurate values [5]. To mitigate this, use strict structured outputs to ensure type-safety [6]. Implement a JSON schema, set the temperature low (0–0.2), and cap retries at 2.

## Common Time Traps and How to Avoid Them

Anticipate bottlenecks before they consume your Saturday.

| Trap | Symptom | When it Bites | Mitigation |
| :--- | :--- | :--- | :--- |
| Data quality issues | Parse errors, nulls | Sat morning | Profile first 200 rows Friday; coerce types. |
| API keys/rate limits | 401/429 errors | Sun morning | Prefer CSVs; prepare static JSON fallbacks. |
| Heavy LLM deps | Brew/apt rabbit hole | Fri night | Use PyMuPDF; avoid Unstructured. |
| Deployment sprawl | CORS, Env var issues | Sun morning | Use static hosting (Netlify/Vercel). |
| Last-minute scope | New "must-have" ideas | Sat afternoon | Freeze scope by Sat noon. |
| Crawl blockers | Unknown robots.txt | Sat morning | Manually curate 50–100 URLs. |

Feature-flagging risky components ensures you always have a working fallback for the demo.

## Minimum Viable Demo Checklists

Each MVP shape must have a crisp story, visible evidence, and a kill switch.

| Shape | Goal | Must-Have Components | Demo Artifacts | Likely Time | Kill Switch |
| :--- | :--- | :--- | :--- | :--- | :--- |
| A. Contracts Dashboard | Show procurement transparency | Socrata CSV ingest; HTML table; filters | 3 prebuilt views (Top vendors, etc.) | 3–5h | Drop charts, ship table-only. |
| B. 311 Router Alpha | Help residents find categories | JSON decision tree; HTML flow; dept links | One polished journey (e.g., pothole) | 4–6h | Ship 10 leaves and 1 path only. |
| C. RVA.gov Micro Search | Find relevant info fast | Curate 50 URLs; JSON extract; Lunr.js | Live search with highlighted matches | 3–5h | Index only titles and H1/H2. |
| D. Storyboard | Stitch A+B+C into one journey | Router result → docs → related contracts | 90s story: issue → dept → contracts | 3–5h | Hard-code 3 examples if linking fails. |
| E. LLM Assist (Stretch) | Add AI safely | PyMuPDF upload; LLM normalize to JSON | Single happy-file demo | 2–4h | Show plain text extraction only. |

Shape A (Contracts Dashboard) is the most reliable anchor, leveraging the City's existing Procurement Transparency initiatives [9].

## Build Plan and Task Allocation

Parallelize work by competency and guard risky items behind feature flags.

* **Friday (3–4h):** PM/UX locks the 311 taxonomy and demo script. Dev 1 ingests the City Contracts CSV and profiles the data. Dev 2 builds the HTML shell and Lunr.js scaffolding.
* **Saturday (10–12h):** Dev 1 finishes the contracts table and filters. Dev 2 implements the 311 router. Dev 3 curates URLs and builds the search index. PM/UX polishes content.
* **Sunday (4–5h):** Polish UI, conduct 3 dry runs, deploy the static site, and stash screenshots as backups.

## Decision Framework

Use simple gates tied to demo readiness to decide when to cut scope.

| Area | Gate (Saturday 12 PM) | If Pass (Push) | If Fail (Cut) |
| :--- | :--- | :--- | :--- |
| City Contracts | Table loads 200+ rows with filters | Add saved views | Ship table-only; no charts |
| 311 Router | 1 polished path + 10+ leaves | Add 2 more paths | Freeze at 10 leaves |
| Search | 50+ pages indexed; fast queries | Add highlights | Title-only index; trim to 30 pages |
| LLM | <10% schema failures on tests | Keep retries | Turn off; show static extraction |
| SAM.gov | Live key + stable responses | Add 1 live card | Static JSON only |

Do not fall for sunk-cost fallacies; if a feature fails its gate, cut it immediately.

## Risk Register

Anticipate skepticism and technical failures by preparing offline proof.

* Save screenshots of the Open Data portal and Procurement Transparency page [9].
* Keep a local CSV snapshot of the City Contracts data [7].
* Maintain a static JSON file for the search index.
* Prepare a specific, pre-tested PDF for the extraction demo.

## Demo Script

Tell one compelling 90-second story that highlights civic value.

* **Beat 1 (Resident):** "I have a pothole." The router maps the issue to Public Works and provides a direct link [8].
* **Beat 2 (Information):** The micro-search instantly surfaces the most relevant Public Works guidance page.
* **Beat 3 (Transparency):** The contracts dashboard displays active roadway maintenance contracts and top vendors, proving the city is actively managing the issue [1].

## References

1. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
2. *Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/Payment-Register-FY16-/kede-pxas
3. *Quickstart - Unstructured*. https://docs.unstructured.io/open-source/introduction/quick-start
4. *Tutorial - PyMuPDF documentation*. https://pymupdf.readthedocs.io/en/latest/tutorial.html
5. *Structured Outputs not reliable with GPT-4o-mini and GPT-4o - API - OpenAI Developer Community*. https://community.openai.com/t/structured-outputs-not-reliable-with-gpt-4o-mini-and-gpt-4o/918735
6. *Structured model outputs | OpenAI API*. https://developers.openai.com/api/docs/guides/structured-outputs/
7. *https://data.richmondgov.com/resource/xqn7-jvv2.csv*. https://data.richmondgov.com/resource/xqn7-jvv2.csv
8. *| Richmond*. https://www.rva.gov/
9. *Procurement Transparency Dashboard | Richmond*. https://www.rva.gov/procurement-services/procurement-transparency-dashboard