
# Building Around Blind Spots — Practical Workarounds for a Thriving Richmond City Hall Hackathon

## Executive Summary

For a Richmond Civic Hackathon team tackling the "A Thriving City Hall" pillar, the absence of live APIs and pre-staged datasets is not a roadblock—it is the core design constraint. The post-2018 blackout of RVA311 data shifts the success criteria from "data science" to "UX and telemetry." Because the City's current AvePoint platform lacks a public API, teams cannot rely on live request volumes, resolution rates, or routing logic to train prioritization models. 

However, a highly functional MVP is entirely feasible if teams pivot to building UX-first, data-pluggable prototypes. By triangulating proxies—such as pre-2018 Socrata datasets, RVA311 UI cues, and Virginia-wide procurement portals—teams can reconstruct enough context to build a resident-facing navigation wizard and a credible contract parsing tool. The winning strategy is to treat the hackathon app itself as an analytics probe: instrumenting the tool to capture the exact telemetry (clickstreams, failed intents, hand-offs) that the City currently lacks. 

This report outlines the five critical information gaps, their impact on hackathon feasibility, and the strategic workarounds required to deliver a working, assumption-transparent product.

## Gap-by-Gap Feasibility Summary

The following table summarizes the critical gaps, their impact on the hackathon, practical workarounds, and the assumptions teams must accept to move forward.

| Gap | Impact Rating | Practical Workarounds (MVP-friendly) | Assumptions You Must Accept |
| --- | --- | --- | --- |
| **1. Post-2018 RVA311 data** (no public API/Socrata for AvePoint) | Critical | Use pre-2018 Socrata SeeClickFix data to seed intents; manually enumerate current request types from RVA311 portal UI; instrument your tool to collect its own query/failure telemetry. | Category volumes and resolution rates are proxies; today's taxonomy may differ from pre-2018 labels; no guarantee of ongoing scraping viability. |
| **2. Pre-staged procurement PDFs** | High | Pull sample contract PDFs from Virginia eVA, VITA Cobblestone, Richmond City Council Legistar, and neighboring localities (Henrico, Chesterfield); curate a 20–30 PDF corpus. | Richmond's templates will be similar to Virginia-standard clauses but may diverge; field positions and headers vary widely. |
| **3. rva.gov analytics and content inventory** | High | Use proxies: historical 311 categories, RVA311 UI "Quick Start" lists, site search cues, and Google Trends; build your own analytics for top queries and zero-result terms. | Proxies may not reflect current seasonality; zero-result terms in your app do not equal sitewide failures. |
| **4. 311 routing decision logic undocumented** | High | Reconstruct v1 from RVA311 request forms, rva.gov department "Helpful Links," and historical request narratives; add an "I'm not sure" catch-all that routes to CSR. | Routing coverage will be partial; edge cases will slip; department ownership can change without notice. |
| **5. VITA contract portal data structure** (no API) | Medium | Use portal filters (SWaM, keyword, category list) and a headless browser to capture list/detail pages to CSV; expose a manual "upload latest VITA CSV" in your tool. | Scraping may break on UI changes/rate limits; field consistency across categories is imperfect; attachment availability varies. |

*Key Takeaway: Success hinges on designing for assumptions, instrumenting your own analytics, and using Virginia-adjacent substitutes where Richmond-specific data is missing.*

## Gap 1: Post-2018 RVA311 Data Blackout — Build UX-first, Data-pluggable Prototypes

### The Missing Data and Its Implications
Richmond's open data portal only exposes pre-2018 SeeClickFix-era 311 requests [1] [2]. The current AvePoint Citizen Services platform offers no public API, and the Open Data portal lists no live 311 datasets [3] [4]. While the RVA311 portal publicly displays request statuses such as "Unprocessed," "Assigned," "In Progress," "On Hold," and "Completed" [5] [6], the underlying data cannot be queried. 

This blackout means prioritization weights and SLAs cannot be validated today. Teams that attempt to build machine-learning triage models on stale 2014 distributions or brittle UI-scraped types will misroute today's issues. 

### Workarounds and Actions
* **Seed Intents from Historical Data**: The 2014 dataset shows consistent, high-frequency maintenance categories recurring across neighborhoods, such as "Potholes," "Trash/Bulk Pick-ups," "Overgrown Lots," and "Illegal Dumping" [2]. Weight your first 10–15 intents on these evergreen service lines.
* **Build a Telemetry Engine**: Prioritize a resident-facing navigation wizard that captures your own analytics from day one (clickstreams, failed intents, hand-offs). 
* **Version the Taxonomy**: The AvePoint platform is configurable, and Richmond's live categories can evolve. Introduce a versioned taxonomy file (JSON) and a lightweight "Admin remap" UI so non-engineers can adjust category names and routing targets without redeploying code.

## Gap 2: Procurement PDFs Not Pre-staged — Use Virginia-native Substitutes

### The Missing Data and Its Implications
The hackathon rubric notes that "sample procurement PDFs not pre-staged" is a gap for the procurement problem. Without representative contract documents, PDF extraction tools cannot be tested or demoed reliably on Richmond-native documents.

### Workarounds and Actions
A strong demo is feasible with Virginia-sourced PDFs. You must be explicit about generalization limits to Richmond's specific templates.
* **Curate a Proxy Corpus**: Assemble a curated 20–30 PDF corpus spanning RFPs, awards, and contract amendments from alternative sources.
* **Leverage Regional Portals**: Pull sample contract PDFs from the VITA Cobblestone portal (where contract attachments are often present) [7], Richmond City Council Legistar agenda attachments, and neighboring localities like Henrico and Chesterfield [8].
* **Parser Approach**: Use heuristic and layout-aware parsing (PDF text blocks + regex + table extraction) targeting standard fields: vendor, award amount, term/dates, renewal options, and SWaM status. Call out which fields are Virginia-standard versus locality-specific in your demo.

## Gap 3: Missing rva.gov Analytics — Triangulate Proxies and Create First-party Signals

### The Missing Data and Its Implications
There is no public data on which rva.gov pages get the most traffic, which searches fail most often, or which departments generate the most resident confusion. This obscures which pages to optimize and hampers proving resident impact.

### Workarounds and Actions
Missing web analytics does not block prioritization if you triangulate proxies to stand in for the missing data.
* **Leverage Site Search Cues**: The rva.gov internal search surfaces high-intent pages prominently. For example, queries for "property search" yield direct links to the Property Search and Property Transfer applications [9]. 
* **Use RVA311 UI Cues**: The RVA311 portal features a "Quick Start Requests" section and a "View All Requests" list for the last 3 months [5] [6], which can serve as a proxy for current high-volume needs.
* **Instrument Your Own Search**: Seed your Information Architecture (IA) with these proxies and instrument your tool's on-site search to immediately generate your own top queries and zero-result terms. Deliver a simple dashboard CSV export that the City can adopt immediately.

## Gap 4: Undocumented 311 Routing Logic — Reconstruct with Public Breadcrumbs

### The Missing Data and Its Implications
The decision tree that maps resident issues to categories and departments is not publicly documented. This risks mis-triage and resident ping-pong between departments.

### Workarounds and Actions
While undocumented, 70–80% of routing paths can be reconstructed from public breadcrumbs.
* **Map Department Ownership**: Use the RVA311 "Helpful Links" page to map responsibilities. For example, the Department of Public Works (DPW) handles Urban Forestry, Paving, and Solid Waste, while the Assessor of Real Estate handles the Property Search Database [10]. 
* **Analyze Historical Narratives**: Historical ticket narratives frequently mention handling units (e.g., DPW, Code Enforcement, Stormwater Mgmt) [2], providing strong hints of the decision tree.
* **Draft a v1 Decision Tree**: Route core intents to DPW, DPU (water/stormwater/streetlights), Solid Waste, and Code Enforcement. Crucially, add an "I'm not sure" catch-all that routes to a Customer Service Representative (CSR) with captured context.

## Gap 5: VITA Cobblestone Data Structure — Semi-automated Extraction

### The Missing Data and Its Implications
VITA statewide contracts are accessible via the Cobblestone web portal, but there is no API or bulk export feature [7]. This limits automation for a cross-source contract comparison tool.

### Workarounds and Actions
The VITA portal is navigable, but scraping is brittle. Plan for semi-automated extraction.
* **Map Visible Fields**: The public Cobblestone portal exposes filters for SWaM status (e.g., Micro Business, Minority Owned, Woman Owned), Keyword search, and detailed VITA Contract Categories (e.g., Hardware, Cloud Services, IT Contingent Labor, Citizen Facing Websites/Applications) [7].
* **Headless Scraper MVP**: Build a headless-browser scraper with throttling for a one-time harvest. Cache the results to CSV/JSON.
* **Manual Refresh Flow**: Implement a manual "Upload latest VITA export" button in your comparison tool. For production, propose an MOU or FOIA-export for periodic data pulls.

## Summary: What You Can Confidently Build vs. What Requires Assumptions

To succeed, teams must clearly delineate what is functional today versus what requires City partnership to harden.

**What the team CAN confidently build now:**
* A 311 navigation wizard with synonym search and "Helpful Numbers" hand-offs (based on public RVA311 UI and department pages).
* A versioned taxonomy and admin remap UI that requires no external dependencies.
* A telemetry pipeline to own analytics from the first click.
* A procurement PDF extractor trained on VA-sourced documents (eVA, VITA, Legistar, neighbors).
* A cross-source comparison tool shell with manual CSV upload for VITA harvests.

**What requires assumptions or proxies:**
* Category prioritization and SLA benchmarks (assumed from historical 2014 data and UI sampling).
* Full routing decision logic (reconstructed for 70–80% coverage; relies on catch-alls for the rest).
* rva.gov top pages and failed searches (relies on proxies and your own app's telemetry).
* Sustained VITA data refresh (assumes manual updates until an export agreement exists).

## Validation and Risk Plan

Anticipate "but what about..." questions from judges by making your assumptions explicit and showing an ops plan for brittle integrations.
* **Assumption Registry**: Clearly display your assumptions in the UI (e.g., "Routing v0.4 last updated Mar 2026"). Document the taxonomy version, category weights source, and routing ownership notes.
* **Smoke Tests**: Implement daily checks to ensure that portal selectors still resolve and validate CSV schemas.
* **Privacy Notes**: Include a telemetry collection disclosure ensuring no PII is stored without consent.

## Demo Narrative

Demonstrate end-to-end value to a resident today while showing the City exactly what data would unlock next-level performance.
1. **Resident Experience**: A resident enters "missed trash pickup." The wizard guides them to the correct category, shows prep tips, and captures the telemetry.
2. **Admin Experience**: The admin dashboard shows the taxonomy editor and live analytics (top intents, zero-results), proving the value of the telemetry engine.
3. **Procurement Parsing**: Parse 3 VA-sourced PDFs, show extracted vendors, amounts, and dates, and flag low-confidence OCR fields.
4. **VITA Comparison**: Show a preloaded CSV filtered by SWaM and category [7], display attachment links, and explain the manual refresh path.

## Appendix — Evidence Pointers

No special access is required to run this MVP. All proxies are derived from public sources:
* **RVA311 Portal**: Exposes request entry, FAQs, and status states (Unprocessed, Assigned, In Progress, On Hold, Completed) [5] [6].
* **Open Data Portal**: Legacy SeeClickFix-era CSVs (2014 sample) provide categories, timestamps, and geos [1] [2].
* **Helpful Links**: Department ownership clues for routing (e.g., DPW for Solid Waste) [10].
* **VITA Cobblestone**: Visible filters for SWaM and detailed contract categories; vendor lists [7].
* **rva.gov Search**: Recurring "Property Search" and "Property Transfer" results signal high-intent topics [9].

## References

1. *New Datasets | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/New-Datasets/uvs3-g9ps
2. *https://data.richmondgov.com/api/views/vgg4-hjn8/r...*. https://data.richmondgov.com/api/views/vgg4-hjn8/rows.csv?accessType=DOWNLOAD
3. *Open Data Portal | Richmond*. https://www.rva.gov/information-technology/open-data-portal
4. *Open Data Portal | Richmond*. https://rva.gov/index.php/information-technology/open-data-portal
5. *Fetched web page*. https://www.rva311.com/rvaone#/request/new
6. *Fetched web page*. https://www.rva311.com/rvaone#/faq
7. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/
8. *FOIA | Richmond*. https://www.rva.gov/911/foia
9. *Search | Richmond*. https://www.rva.gov/search?search=property%20search&page=0
10. *RVA 311 Helpful Links | Richmond*. https://www.rva.gov/citizen-service-and-response/rva-311-helpful-links