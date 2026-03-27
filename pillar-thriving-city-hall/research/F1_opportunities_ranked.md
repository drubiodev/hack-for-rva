---
title: "Richmond City Hall Hackathon — Fastest Paths to High-Impact, Adoptable Tools"
pillar: thriving-city-hall
section: F
problem_statement: general
tags:
  - opportunities-ranked
  - contract-expiry
  - 311-helper
  - service-pathway
  - feasibility
  - adoption
summary: "Ranked evaluation of seven City Hall solution spaces on data readiness, 48-hour feasibility, and adoption potential. Recommends Contract Expiry Dashboard as top build; Plain-Language 311 Helper and Service Pathway Mapper as alternatives."
geography: Richmond, VA
source: parallel-ai-pro
status: raw
related_reports:
  - F2_opportunities_service_nav
  - F3_opportunities_procurement
  - H1_mvp_48hr_framework
---

# Richmond City Hall Hackathon — Fastest Paths to High-Impact, Adoptable Tools

## Executive Summary

To maximize the impact of the "A Thriving City Hall" hackathon pillar, teams must navigate Richmond's specific data realities. The most successful builds will bypass blocked data pipelines and leverage recently updated, structured datasets. 

* **Contract Expiry visibility is a clear, data-ready win:** The City Contracts dataset is public, updated monthly (last updated March 16, 2026), and features clean effective and end dates alongside detailed narratives [1]. We prioritize **D: Contract Expiry Dashboard** as the top build.
* **311 need is strong but data is constrained:** The RVA311 Service Request Management system is active (contracted with AvePoint through December 31, 2026) [2], yet there is no public post-2018 API. Scope **A: Plain-Language 311 Helper** to static logic and decision trees rather than machine learning.
* **Residents face fragmented "how-to" journeys:** Service content exists but is scattered across the Services directory, Permits & Inspections pages, and various PDF guides [3] [4] [5]. **C: Service Pathway Mapper** offers a low-risk, high-clarity alternative.
* **PDF contract extraction is compelling but blocked:** **E: PDF Contract Extractor** requires pre-staged PDFs with varied structures. None are currently available, and the City Contracts dataset does not expose document links. Avoid this unless sample contracts are secured pre-event.
* **"Transparency dashboards" risk duplication:** Richmond already hosts a Procurement Transparency page pointing to the City Contracts dataset [1] [6]. **G: Government Transparency Dashboard** must focus on new angles (e.g., upcoming expirations) to avoid duplicating existing tools.

## Why These Seven Ideas — And How We'll Pick Winners

We evaluate the seven proposed solution spaces (A–G) based on documented need, data readiness, 48-hour feasibility, demo clarity, and adoption potential. The goal is to identify which projects can transition from a weekend prototype to an adopted City Hall tool.

### Richmond-Specific Constraints That Shape Feasibility

Three critical local constraints dictate what can actually be built and adopted in 48 hours:
* **311 Limitations:** There is no post-2018 public API for 311 data, but there is a strong internal champion (Pete Breil) and an active SRM contract [2].
* **Contract Data Strengths:** The City Contracts dataset is a clean Socrata CSV with end dates [1]. While it lacks a named "champion" in the prompt, it has clear ownership.
* **PDF Unavailability:** There are no pre-staged PDF documents available for extraction, and staging is required pre-build to make LLM extraction viable.

## Data Readiness Deep-Dive — What's Actually Usable Day 1

### Contracts: Monthly-Updated CSV/API With End Dates

The City Contracts dataset (xqn7-jvv2) is highly accessible and ready for immediate use. It was last updated on March 16, 2026, and has garnered 18K views and 21.3K downloads [1]. The data is provided by the Department of Procurement and includes critical fields such as agency name, contract dollar amount, supplier name, and effective start and end dates [1]. This makes filtering by expiry and amount achievable with zero ETL overhead.

### Spend and Budget: Payment Register and General Fund

Richmond's Open Data Portal hosts the Payment Register FY16+ and City Budget - General Fund datasets [7] [8]. These are sufficient for building supplier concentration and trend views, allowing a transparency dashboard to add unique "what's next" predictive views rather than just generic historical spend charts.

### Federal and State Procurement: SAM.gov API and eVA CSV

For cross-source querying, the SAM.gov Get Opportunities Public API allows filtering by state and zip code, though it restricts the posted date range to a 1-year window [9]. Additionally, the eVA procurement data for 2024 is available as a downloadable CSV via the Virginia Open Data Portal [10]. This allows for federated queries, though entity resolution across these datasets should be postponed.

### RVA.gov Content Landscape: Acquia/Drupal and Key Guidance PDFs

RVA.gov is hosted in the cloud via Acquia (under a Carahsoft contract running through December 19, 2026) [2]. The site contains abundant but fragmented guidance, including the Homeowners Residential Building Permit Process Guide and the Online Permit Portal User Guide [4] [11]. This crawlable content is ripe for smart search indexing and curated pathway mapping.

## Buildability in 48 Hours — Scope to Ship

To ensure a working demo by Sunday, teams must align their skills with the minimum viable feature set of each solution space.

| Solution | Critical Dependency | Blocking Risk | Minimum Viable Feature Set | Team Skill Emphasis |
| :--- | :--- | :--- | :--- | :--- |
| **A: 311 Helper** | Public FAQs + champion time | Low (no API needed for static) | Decision tree for ~50 request types; intake copy; routing links | UX writing, front-end |
| **B: Smart Search** | Targeted crawlable sections | Medium (scope bloat) | Index 3–5 sections; synonyms; type-ahead | Search/crawl, devops |
| **C: Pathway Mapper** | Curate 8–10 journeys | Low | Step-by-step flows w/ links, timelines, costs | Service design, content |
| **D: Expiry Dashboard** | Socrata CSV/API | Low | Filters by expiry window, agency, amount; CSV export | Data viz, front-end |
| **E: PDF Extractor** | 10–20 sample PDFs | High (no docs available) | Extract terms (supplier, term, amount); error handling | NLP/LLMs, parsing |
| **F: Cross-Source Finder** | API keys; CSV pulls | Medium (joins) | Federated search across City/SAM/eVA; saved filters | API integration |
| **G: Transparency Dash** | Framing vs existing tools | Medium (duplication) | New lens: expirations, supplier concentration | Data viz, analysis |

*Takeaway: Solutions D, A, and C offer the highest confidence for a 48-hour build. E is highly risky without pre-staged inputs.*

## Demo Clarity — 5-Minute Stories That Land

A successful hackathon pitch relies on immediate, recognizable value. Prioritize "question-to-answer" flows and countdowns to action.

* **A (311 Helper):** Type "pothole" → plain-language steps + link to submission.
* **B (Smart Search):** Search "bulk trash" → surface the exact right page vs. the current search experience.
* **C (Pathway Mapper):** "Start a business" → 8 clear steps with costs and timeline.
* **D (Expiry Dashboard):** "What expires in 90 days over $1M?" → sortable list + CSV export.
* **E (PDF Extractor):** Upload contract → auto-highlight term, renewals (only viable if PDFs are staged).
* **F (Cross-Source Finder):** "Stormwater NAICS in VA, posted last 90 days" → side-by-side hits.
* **G (Transparency Dash):** "Top 10 suppliers and expirations next 6 months" → risk view.

## Adoption Potential — Champions, Owners, and Continuity

Post-hackathon adoption hinges on internal champions. Anchor builds to Citizen Service & Response (CSR) and Procurement.

| Solution | Likely Champion/Owner | Evidence | Adoption Lever | Next Step |
| :--- | :--- | :--- | :--- | :--- |
| **A: 311 Helper** | Pete Breil (CSR) | Stated strong champion; active SRM contract [2] | Reduce call load; better self-service | Book day-1 validation |
| **D: Expiry Dash** | Michael Gordon (Procurement) | Listed as dataset owner [1] | Renewal planning; workload smoothing | Share mockups pre-demo |
| **B/C: Search/Map** | Dept. web owners (PDR, Finance) | Acquia hosting [2]; many guides [4] | Reduce help calls; clearer journeys | Identify 3 content stewards |
| **F/G: Procurement** | Procurement + Finance | Transparency page exists [6] | Market intelligence; trust | Position unique insights |

*Takeaway: Pre-wire 15-minute validation sessions with these owners to lock in adoption potential.*

## Risks, Edge Cases, and Mitigations

Predefine kill-switches and pivots to avoid stalled demos during the 48-hour window:
* **E stalls without PDFs:** Pivot to D or C by T-24h if documents cannot be sourced.
* **B underwhelms if corpus is too broad:** Narrow the index to 3–5 high-traffic sections and add synonym dictionaries.
* **G duplicates existing dashboards:** Reframe the visualization entirely to focus on expirations and supplier concentration risk.
* **F returns noisy results:** Ship saved filters, label sources plainly, and explicitly postpone entity deduplication to a future roadmap.

## Scoring Matrix and Ranking Plan

The following matrix ranks the solutions based on the five requested dimensions (scored 1=low, 5=high), tuned to Richmond's specific constraints.

| Rank | Solution | Evidence | Data | Buildability | Demo Clarity | Adoption | Total Score | Richmond-Specific Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **D: Expiry Dashboard** | 4 | 5 | 5 | 5 | 4 | **23** | Socrata contracts ready [1]; owner listed [1]; no named champion. |
| **2** | **C: Pathway Mapper** | 4 | 4 | 5 | 5 | 4 | **22** | Abundant guides RVA.gov [4] [11]; high clarity. |
| **3** | **A: 311 Helper** | 5 | 2 | 4 | 5 | 5 | **21** | No post-2018 API; strong champion; use decision trees. |
| **4** | **F: Cross-Source Finder** | 4 | 4 | 3 | 4 | 3 | **18** | SAM (1-yr window) [9], eVA CSV [10], City Socrata [1]; federate only. |
| **5** | **B: Smart Search** | 4 | 3 | 3 | 4 | 3 | **17** | Acquia/Drupal [2]; scope narrowly to shine. |
| **6** | **G: Transparency Dash** | 3 | 4 | 3 | 3 | 3 | **16** | Avoid duplicating existing transparency page/dashboard [6]. |
| **7** | **E: PDF Extractor** | 3 | 1 | 2 | 4 | 2 | **12** | No staged PDFs; highly risky without inputs. |

*Takeaway: D ranks first due to flawless data readiness and buildability. A ranks high on adoption but is penalized on data availability. E is gated by missing inputs.*

## Recommendations

### Top Recommendation: D - Contract Expiry Dashboard
**Rationale:** This is the fastest path to impact with clean, timely data. The City Contracts dataset is updated monthly and contains the exact fields needed (effective start and end dates) [1]. It provides immediate, tangible value to the Department of Procurement for renewal planning and workload smoothing, requiring zero complex data engineering.

### Second-Choice Recommendations by Skill Profile
* **For Content/UX-Heavy Teams:** **A (Plain-Language 311 Helper)** or **C (Service Pathway Mapper)**. These require minimal backend engineering but rely heavily on service design, UX writing, and static logic to solve real resident pain points.
* **For Search/Integration-Heavy Teams:** **B (RVA.gov Smart Search)** or **F (Cross-Source Contract Finder)**. These leverage APIs and crawling capabilities to unify fragmented information, providing a strong technical showcase.

## 48-Hour Execution Plan

To ensure success, teams should adhere to the following milestone schedule:

| Time | Milestone | Success Metric |
| :--- | :--- | :--- |
| **H+4** | Data access locked | API calls succeed; sample rows cached (Socrata, SAM key, eVA CSV). |
| **H+12** | First vertical slice | One end-to-end query/view works. |
| **H+18** | Champion review | 3+ changes incorporated from feedback (A/D/C). |
| **H+30** | Usability pass | 5-person hallway test complete. |
| **H+40** | Demo script locked | 2-minute and 5-minute flows rehearsed. |
| **H+46** | Contingency pivot check | Kill-switch criteria met or not needed. |
| **H+48** | Final demo | Crisp story, zero live data fragility. |

*Takeaway: Timebox scoping strictly. Lock data access by hour 4 and validate with champions by the end of day 1 to guarantee a polished, adoptable product.*

## References

1. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
2. *https://data.richmondgov.com/resource/xqn7-jvv2.csv*. https://data.richmondgov.com/resource/xqn7-jvv2.csv
3. *Permits and Inspections | Richmond*. https://www.rva.gov/planning-development-review/permits-and-inspections
4. *Homeowners Residential Building Permit Process Guide*. https://www.rva.gov/sites/default/files/2025-05/Homeowner%27s%20Permit%20Process%20Guide_2021%20VRC.pdf
5. *Services | Richmond*. https://rva.gov/common/services
6. *Procurement Transparency Dashboard | Richmond*. https://rva.gov/procurement-services/procurement-transparency-dashboard
7. *Open Data Portal | City of Richmond, Virginia | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/
8. *City Budget - General Fund | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Budget-General-Fund/7nru-hsrx
9. *SAM.gov Get Opportunities Public API | GSA Open Technology*. https://open.gsa.gov/api/get-opportunities-public-api/
10. *eVA Procurement Data 2024 - Virginia - Dataset - Virginia Open Data Portal*. https://data.virginia.gov/dataset/eva-procurement-data-2024
11. *City Of Richmond Online Permit Portal User Guide*. https://www.rva.gov/sites/default/files/2019-12/OPP%20User%20Guide.pdf