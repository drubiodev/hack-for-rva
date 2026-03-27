---
title: "Closing Richmond's Civic UX Gap: Faster Service Discovery and Smarter Contract Review"
pillar: thriving-city-hall
section: context
problem_statement: general
tags:
  - service-navigation
  - procurement
  - rva.gov
  - RVA311
  - City Contracts
  - Socrata
summary: "Executive overview of both City Hall problem domains: residents cannot navigate rva.gov and RVA311 to find services, and city staff must manually review contracts across four disparate platforms. Establishes key system architecture facts and top hackathon priorities."
geography: Richmond, VA
source: parallel-ai-pro
status: raw
related_reports:
  - A1_problem_landscape_service_navigation
  - A2_problem_landscape_procurement_review
---

# Closing Richmond's Civic UX Gap: Faster Service Discovery and Smarter Contract Review

## Executive Summary

Richmond faces two distinct but structurally similar challenges: fragmented information architecture that hinders user success. For residents, discovering city services is blocked by a department-centric website (rva.gov) that is disconnected from the actual service request system (RVA311). For city staff, evaluating procurement contracts requires hunting across four disparate platforms (City, State, Federal, and eVA) and manually extracting terms buried in PDF attachments. 

**Key Facts:**
* **Resident Systems:** rva.gov operates on Drupal 8+ with over 40 department slugs and uses a Drupal Search API with Facets. RVA311 runs on AvePoint Citizen Services (Dynamics 365) and lacks a public API.
* **Procurement Systems:** City contracts are available via Socrata OData (xqn7-jvv2) [1]. eVA data is available as massive CSV exports (the 2024 file is 1 GiB with over 1.9 million rows) [2]. SAM.gov requires an API key with strict rate limits [3] [4]. VITA contracts have no API.

**Key Inferences (Labeled):**
* *Inference:* Because historical 311 data (SeeClickFix) ends in August 2015 and RVA311 has no public API, hackathon teams cannot rely on live or recent time-series data to build predictive 311 models.
* *Inference:* Because critical contract clauses are locked in PDFs across multiple portals, a unified search tool will only be valuable if it includes automated PDF text extraction.

**Top Hackathon Priorities:**
1. **Build a Resident-Centric "Service Finder":** Map common intents to next steps across both systems using a lightweight content index.
2. **Stand up a Procurement ETL Pipeline:** Unify City OData, eVA CSV, and SAM.gov API data into a single searchable database.
3. **Implement PDF Clause Extraction:** Use OCR/text extraction to pull key terms (vendor, value, dates) from contract attachments.

## Problem Framing: Two high-value UX gaps limit city effectiveness

Residents cannot reliably find next steps, and staff cannot efficiently compare contracts due to fragmented systems and document-heavy workflows.

### Resident Service Discovery Is Department-Centric, Not Task-Centric
Richmond's city information architecture forces residents to understand the city's internal organizational chart to find services. Content exists but is not organized by resident intent, splitting answers across rva.gov (which has over 40 department slugs) and RVA311. This creates a high-friction experience that likely drives up abandonment rates and unnecessary phone calls to the 311 call center.

### Procurement Review Is Multi-Source and Document-Heavy
City staff must evaluate contracts from multiple sources to ensure compliance, find the best pricing, and manage renewals. However, critical terms are scattered across City, state, and federal systems. Furthermore, the actual details of these agreements are often buried in PDF attachments rather than structured database fields, slowing down reviews and making cross-contract comparison nearly impossible without manual data entry.

## Current Systems and Data Landscape: What exists, where it lives, and how to access it

Hackathon teams can reach most data today via OData, CSV, and REST APIs, with the notable exceptions of RVA311 and VITA. 

### Resident-Facing Systems
rva.gov and RVA311 are complementary but not integrated for developers. Historic 311 data is too dated for modern trend analysis.

| System / Dataset | Platform / Format | Access & Limitations | URL / Source |
| :--- | :--- | :--- | :--- |
| **rva.gov** | Drupal 8+ on Acquia | Department-centric (40+ slugs); Drupal Search API with Facets; Google Translate (36 languages). | https://rva.gov |
| **RVA311** | AvePoint on Dynamics 365 | Launched June 2018; **No public API**. | Vendor product / City pages |
| **Historic 311** | Socrata (vgg4-hjn8) | SeeClickFix data; Coverage limited to Jan 2014–Aug 2015. | https://data.richmondgov.com |

*Takeaway:* Teams should avoid building predictive models on the outdated SeeClickFix data and instead focus on scraping and structuring the content currently available on rva.gov.

### Procurement Data Sources
City OData, eVA CSV, and the SAM API can be integrated into a unified backend. VITA is web-only and will require workarounds.

| Source | Format / Access | Key Details & Limitations | URL / Source |
| :--- | :--- | :--- | :--- |
| **City Contracts** | Socrata OData (xqn7-jvv2) | 9 columns; updated monthly; last updated Mar 2, 2026 [1]. All 9 columns returned correctly via API (corrected 2026-03-18 — prior "column bug" claim was incorrect). | http://data.richmondgov.com/widgets/xqn7-jvv2 [5] |
| **eVA (Virginia)** | CSV Export | 2024 dataset: 44 columns, 1,922,754 rows, 1 GiB [2]. | http://data.virginia.gov/dataset/eva-procurement-data-2024 [6] |
| **SAM.gov (Federal)** | REST API | Requires API key; strict rate limits apply [3] [4]. Attachments via `resourceLinks` [3]. | http://open.gsa.gov/api/get-opportunities-public-api [3] |
| **VITA (State)** | Web Portal | **No API**. Requires manual scraping or uploads. | vita.cobblestonesystems.com/public/ |

*Takeaway:* A successful procurement tool must handle massive CSV ingestion (eVA) alongside rate-limited API calls (SAM.gov) and OData streams (City).

## Comparable Models: What leading cities do differently

Leading municipalities expose service knowledge via APIs, not just through traditional search bars, enabling third-party integrations.

### NYC's 311 Content API Enables Task-Centric Responses
New York City offers a dedicated NYC311 Content API (JSON format, registration required) that increases access to 311 online content [7]. This API-first approach allows developers to create applications that answer "what do I do?" with structured steps, improving transparency and accountability [7].

### NYC Open Data + SoQL for 311 Requests
NYC also provides open access to 311 Service Requests through Socrata APIs and the Socrata Query Language (SoQL) [8]. This allows developers to filter, map, and export service requests [8], supporting analytics and routing prototypes that Richmond currently cannot support due to its closed RVA311 system.

## Data Limitations, Risks, and Unknowns: Build eyes-open to gaps

Two hard constraints—no RVA311 API and no VITA API—plus the reliance on PDFs and strict API budgets require defensive engineering, caching, and extraction strategies.

### API Limits and Access
Teams integrating federal data must plan for SAM.gov rate limits and schema drift.

| User / Connection Type | Authentication | Default Rate Limit |
| :--- | :--- | :--- |
| Non-federal user with no role | Personal API key | 10 requests/day [4] |
| Non-federal user with a role | Personal API key | 1,000 requests/day [4] |
| Non-federal system | System account API key | 1,000 requests/day [4] |
| Federal system | System account API key | 10,000 requests/day [4] |

*Takeaway:* Hackathon teams using personal API keys without specific roles will be capped at just 10 requests per day [4], making local caching of SAM.gov responses absolutely critical for development and demonstrations.

### Unknowns (What cannot be verified publicly)
* **RVA311 Export Options:** It is unknown if internal bulk access or an authenticated feed can be provided to teams during the hackathon.
* **City API Bug:** No column bug exists on the City Contracts dataset (xqn7-jvv2) — the API returns all 9 columns correctly (corrected 2026-03-18).
* **VITA Scraping Tolerance:** It is unknown if the VITA portal has anti-bot controls that would block automated scraping attempts during the event.

## Opportunity Areas and Solution Concepts: What to build now

Two Minimum Viable Products (MVPs) can deliver immediate value within a 72-hour hackathon and set foundations for long-term integration.

### Service Finder v1: Intent-led answers across rva.gov and RVA311
A structured content index combined with decision trees can route residents to next steps without needing live 311 data. Teams should build an intent taxonomy (e.g., the top 50 resident tasks), a synonym dictionary, and language-ready snippets leveraging the existing 36-language Google Translate support.

### Procurement Explorer v1: Cross-source contract finder with PDF insights
Teams should build a unified search and filter interface over the City OData, eVA CSV, and SAM metadata. Crucially, this must include a pipeline that downloads attachments (e.g., via SAM's `resourceLinks` [3]) and extracts clauses from PDFs to enable side-by-side contract comparisons.

## Technical Approach: How to deliver in 72 hours

Cache-first ingestion, schema validation, and lightweight UIs will keep scope tight and demos stable.

### Data Ingestion and Document Processing
Connectors should be built for City Contracts via OData (xqn7-jvv2) and eVA CSV streaming. SAM.gov REST calls must be cached immediately due to rate limits. For document processing, teams should implement PDF OCR and text extraction, using regex or lightweight ML to tag contract values, dates, renewals, and vendor names.

### Service Content Extraction and Matching
Teams should crawl rva.gov service pages and normalize them into a standard JSON schema (e.g., `{intent, department, steps, docs, cost, contact, link}`). For procurement, vendor normalization is critical; teams should use fuzzy matching and prefer the Unique Entity Identifier (UEI) where available in SAM.gov data [9].

## Implementation Risks and Mitigations

Brittle demos are the biggest risk. Teams must use schema tests, caches, and manual fallbacks to handle rate limits and site changes.
* **Mitigations:** Implement scheduled nightly pulls rather than live queries; run schema diff tests on xqn7-jvv2 to catch any future changes (no column bug currently; API returns all 9 columns; corrected 2026-03-18); rely entirely on cached SAM responses for the frontend; and provide a manual CSV upload option for VITA data in case scraping is blocked.

## Measurement and Validation: Prove impact fast

Teams should define 3–5 success metrics per MVP to prove value during final presentations.

### Service Finder Metrics
Track task success rate, time-to-answer, coverage of the top-20 resident intents, and the completeness of translated language snippets.

### Procurement Explorer Metrics
Measure the time-to-locate key terms compared to manual PDF reading, the number of successfully cross-linked records between City and eVA datasets, and PDF extraction accuracy (precision/recall on a sample set).

## Top 3 Evidence-Based Hackathon Priorities

Focus on tangible, high-leverage builds with open access.

1. **Ship a Service Content API + Finder for 50 intents:** rva.gov content is available, while the RVA311 API is not. Crawl and normalize pages into an intent taxonomy with synonyms and language-ready copy.
2. **Build a Procurement ETL + Explorer:** Data is accessible today via City OData [1], eVA CSV [2], and SAM API [3]. Ingest, cache, unify fields, and execute vendor/contract matching.
3. **Implement a PDF clause extraction pipeline:** Key details are buried in PDFs. Build OCR/text extraction and clause taggers for value, dates, and renewals to create searchable fields.

## Workplan and Roles: 72-hour roadmap

Parallelize ingestion, extraction, and UI work. End each day with a demoable slice.

### Day 1: Foundations
Focus on data connectors, crawling rva.gov, defining JSON schemas for both resident services and procurement, and standing up UI skeletons.

### Day 2: Logic and Integration
Implement vendor matching logic, build the PDF extraction MVP, map out service decision trees, and finalize the SAM API integration (ensuring caching is active to protect the 10-request limit for unauthenticated keys [4]).

### Day 3: Polish and Pitch
Polish the frontends, instrument success metrics, run a validation set for PDF extraction accuracy, and finalize the demo narratives highlighting the UX improvements for both residents and staff.

## References

1. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
2. *eVA Procurement Data 2024 - Virginia - eVA_Procurement_Data_2024(CSV) - Virginia Open Data Portal*. https://data.virginia.gov/dataset/eva-procurement-data-2024/resource/25a59527-f14a-475d-b8da-af0155015887
3. *SAM.gov Get Opportunities Public API | GSA Open Technology*. https://open.gsa.gov/api/get-opportunities-public-api/
4. *System Account User Guide (v2 with non-federal access)*. https://dodprocurementtoolbox.com/uploads/System_Account_User_Guide_v2_with_non_federal_access_82572248c0.pdf
5. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/widgets/xqn7-jvv2
6. *eVA Procurement Data 2024 - Virginia - Dataset - Virginia Open Data Portal*. https://data.virginia.gov/dataset/eva-procurement-data-2024
7. *
	
		
		








  
NYC311 Content API · NYC311
*. https://portal.311.nyc.gov/article/?kanumber=KA-01336
8. *NYC Open Data -   How To*. https://opendata.cityofnewyork.us/how-to/
9. *SAM.gov Opportunity Management API | GSA Open Technology*. https://open.gsa.gov/api/opportunities-api/