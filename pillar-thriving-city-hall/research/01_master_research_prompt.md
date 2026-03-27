# Route Right, Buy Smart: A weekend playbook for RVA311 navigation and procurement risk

## Executive Summary

This research framework provides a strategic baseline for the Richmond Civic Hackathon's "A Thriving City Hall" pillar. Teams tackling Resident Service Navigation and Procurement Risk Review face a common challenge: high-value civic data is locked behind opaque interfaces, department-centric architectures, and unstructured PDFs. 

The most critical finding for hackathon teams is the lack of a public API for Richmond's RVA311 system. While the city uses AvePoint Citizen Services (Dynamics 365) [1], the available AvePoint Graph API targets internal data management and partner operations, not public service request submissions [2]. Therefore, navigation solutions must adopt an "outside-in" approach—curating plain-language guidance and deep-linking users to the correct official RVA311 category rather than attempting to submit requests on their behalf. 

For procurement, contract data is fragmented across Richmond's Socrata portal [3] and the state's VITA CobbleStone public portal [4]. Because the CobbleStone REST API requires authenticated client credentials [5] [6], teams must rely on respectful web scraping and PDF extraction to surface critical risk factors like expiration dates and renewal windows. By leveraging open exemplars like Philadelphia's Contracts Hub [7] [8], teams can rapidly prototype a procurement risk triage dashboard this weekend.

## Context and Objectives

We can materially improve first-try service routing and contract risk visibility without privileged access by curating plain-language guidance and extracting high-value terms from public sources. The objective is to build resident-centric navigation and contract risk triage within strict public-data constraints.

### Systems Landscape and Constraints

The 311 platform lacks a public API for direct submission. RVA311, launched on June 15, 2018 [9] [10], provides a web portal and mobile apps for residents to submit non-emergency requests [11]. However, the underlying AvePoint Citizen Services platform does not expose a public endpoint for third-party applications to push data directly. Contract data spans Richmond Socrata, VITA's web portal, and PDFs; therefore, solutions must be "outside-in" and provenance-heavy.

## Public Data Assets and Access Methods

Combine direct-open datasets (Socrata) with respectful scraping (VITA portal) and curated rva.gov content. Avoid assumptions about non-public APIs.

| Asset | URL / Source | Access Method | Notes & Constraints | Recommended Hackathon Use |
| :--- | :--- | :--- | :--- | :--- |
| **RVA311 Public Portal** | rva311.com | Web UI / App | No documented public API for submissions [11]. | Link-out submission; category mapping. |
| **RVA311 Helpful Links** | rva.gov/citizen-service-and-response/rva-311-helpful-links | Web | Content can drift over time [12]. | Seed knowledge base; verify timestamps. |
| **City Contracts (Socrata)** | data.richmondgov.com (xqn7-jvv2) | API / CSV | Stable SODA endpoint [3]. | Baseline contracts list ingestion. |
| **VITA Contracts Portal** | vita.cobblestonesystems.com/public/ | Web | No public export; pagination required [4]. | Scrape index; fetch attached PDFs. |
| **CobbleStone REST API** | wiki.cobblestonesoftware.com | API (Auth) | Requires client ID/secret [5]. | Not usable publicly; note for future integration. |
| **Philly Contracts Data** | cityofphiladelphia.github.io/contracts/ | Web / CSV | Reusable open data patterns [7] [13]. | Model UI and data schema. |

## Resident Service Navigation

A synonym-driven, "How do I…" navigator that maps to official categories and verifies content freshness can boost first-try accuracy without filing on behalf of residents.

### What's the problem behind the problem

Residents think in tasks, but city websites are organized by departments, creating cognitive translation costs. For example, finding permit information requires navigating through the "Planning and Development Review" department [14]. This department-centric information architecture causes misselection when residents attempt to file 311 requests.

### Winning approaches we can apply now

Curate top intents and map them to official categories. Show previews of requirements and timelines before sending users to RVA311. Teams should build a synonym index for the top 20 intents (e.g., bulk pickup, missed trash, pothole) and display "What you'll need" sourced from rva.gov pages. If confidence is below a certain threshold, the UI should show 2-3 category options with short descriptions.

### Failure modes and guardrails

Use a closed corpus, verification stamps, and a confirm step to keep trust high and prevent confidently wrong AI routing.

| Failure Mode | Why It Happens | Mitigation Strategy |
| :--- | :--- | :--- |
| **Confidently wrong routing** | No ground-truth API; reliance on external ML guessing. | Show top alternatives + "Does this look right?" confirm step. |
| **Stale content** | Drupal pages update independently of the tool. | Nightly link/content checks; display "Verified X days ago". |
| **Hallucinated services** | Generative text risks inventing city services. | Use a closed KB; require citations; disable generation on unknowns. |
| **Privacy leakage** | Sensitive categories (social services, taxes) are private [11]. | Respect privacy notes; avoid deep-linking to private cases without warnings. |

### Measuring impact without internal 311 data

Track confirm rates, clickthroughs to suggested categories, and duplicate-prevention usage as proxy KPIs. Since post-2018 RVA311 data isn't public, teams must instrument their own navigators to log intent-to-category confirmations.

## Procurement Risk Review

Focus on expiration and renewal windows across City and VITA data. Pair extracted terms with human-verifiable snippets to build trust with procurement staff.

### Data ingestion plan

Use SODA for City Contracts [3] and respectful scraping for the VITA portal [4]. Capture provenance everywhere so staff can verify the source of the extracted data.

### Clause extraction

Regex and OCR can achieve 80% accuracy this weekend. Extract terms like Effective Date, Expiration/End Date, Renewal options, and Not-to-Exceed pricing. Output this as JSON with the field, value, confidence score, source URL, and the exact text snippet from the PDF.

### Presenting risk

A single "Expiring/renewal window" queue sorted by department and vendor unlocks quick wins for city staff who currently scan PDFs manually.

## National Exemplars We Can Reuse

Philadelphia's Contracts Hub and datasets provide a working pattern we can adapt quickly. The City of Philadelphia provides open data on professional services and commodities contracts [7] [15], and their Contracts Hub code is available on GitHub [8]. Teams should borrow their data model (vendor, department, term, amount, status) for Richmond.

## Technical Constraints and Workarounds

Design for no-API environments, schema drift, pagination, and OCR variance. Keep an ingestion manifest for reproducibility.

| Constraint | Risk | Practical Workaround |
| :--- | :--- | :--- |
| **No public RVA311 API** | Cannot validate or file requests directly. | Link-out to official portal; map categories; require user confirmation. |
| **VITA portal web-only** | No bulk export available [4]. | Automate browser scraping; cache HTML; implement rate-limiting. |
| **CobbleStone API gated** | Credentials required for access [5]. | Do not rely on it for the hackathon; document as a future state. |

## Estimating Misrouting Without Published Error Rates

Cities rarely publish misroute error rates; use adjacent signals to estimate and improve. Track navigator assists per week and confirm rates. Use the RVA311 map's "nearby requests" feature to help reduce duplicates [11].

## Weekend Build Plan

Ship a usable MVP by Sunday that routes top intents and flags expiring contracts with citations.
* **Day 1:** Scrape/curate top rva.gov pages; build synonym map for top 20 intents. Ingest City Contracts via SODA; prototype VITA portal scraper.
* **Day 2:** Build Navigator UI with confirm flow and deep links. Build PDF extractor for expiration/renewal with snippet capture.
* **Day 3:** Implement verification stamps and error states. Prepare demo with 5 resident journeys and 5 contracts showing extracted terms.

## Risks, Ethics, and Sustainability

Always show sources, time-stamps, and confidence scores. Never imply internal access you don't have, and design the architecture for eventual handoff to City teams.

## Facts, Inferences, and Unknowns

* **Facts:** RVA311 launched in June 2018 [9]. The AvePoint Graph API uses OAuth 2.0 and requires client secrets/certificates [2]. Philadelphia publishes contract data openly [7] [13].
* **Inferences:** (Clearly labeled) *Inference:* A 5% improvement in first-try routing would affect ~10,000 requests/year based on the 2025 volume estimate. *Inference:* Socrata schemas may drift, requiring column ID usage rather than name binding.
* **Unknowns:** Documented misroute error rates for 311 nationally; public post-2018 RVA311 request-level data availability.

## References

1. *RVA 311 | AvePoint*. https://www.avepoint.com/case-studies/rva311
2. *Overview *. https://learn.avepoint.com/docs/Overview.html
3. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
4. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/
5. *REST API Overview*. https://wiki.cobblestonesoftware.com/docs/rest-api-overview
6. *
	Welcome to Contract Insight Documentation Wiki
*. https://insightwiki.cobblestonesystems.com/default.aspx?pg=ywtKfZVqbZMBnkN5Zwl8IA%3D%3D
7. *City of Philadelphia: Open Contract Data*. https://cityofphiladelphia.github.io/contracts/
8. *GitHub - CityOfPhiladelphia/contracts-hub · GitHub*. https://github.com/CityOfPhiladelphia/contracts-hub
9. *Get the 411 on RVA311, the city’s new non-emergency reporting service*. https://www.wtvr.com/2018/06/15/get-the-411-on-rva311-the-citys-new-non-emergency-reporting-service
10. *City launching new RVA311 service today to handle citizen ...*. https://rvahub.com/2018/06/15/city-launching-new-rva311-service-today-to-handle-citizen-business-visitor-requests154627/
11. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
12. *RVA 311 Helpful Links | Richmond*. https://www.rva.gov/citizen-service-and-response/rva-311-helpful-links
13. *Datasets - OpenDataPhilly*. https://opendataphilly.org/datasets/
14. *Permits and Inspections | Richmond*. https://www.rva.gov/planning-development-review/permits-and-inspections
15. *City of Philadelphia: Procurement Commodities Contracts*. https://www.phila.gov/contracts/data/commodities/