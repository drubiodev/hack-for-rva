# No-API, No Problem: Building a Credible RVA311 Navigator

## Executive Summary — A navigation-first MVP can be credible without live RVA311 data

By anchoring to rva.gov content, Open311 schema, and proxy city structures, a hackathon team can deliver accurate routing and instructions while transparently disclaiming the lack of live 311 data. Since June 2018, RVA311 (AvePoint Citizen Services) has operated without a public API and stopped publishing to Socrata. While 2025 volume data is visible in news reports, it is not queryable via public endpoints. Therefore, the MVP must be treated as a navigation and triage tool "based on public City content," rather than a live-data dashboard. Prioritizing accurate routing, clear instructions, and standards-based data structures will yield a highly functional prototype despite the constraints.

## Constraint Landscape — No post-2018 API means no live categories or cases

Treat the absence of an API as a design constraint: focus the MVP's value on service discovery, routing, and user guidance rather than analytics. 

The current RVA311 system's data is completely inaccessible publicly. What is available from verified sources: in 2024, the city received ~203,000 calls and ~75,200 requests created (corrected 2026-03-18 — previously cited 208,216 was incorrect) [1]. Call center agents resolved a large share of concerns over the phone without having to create a request for specific departments [1]. Because post-2018 case data and the current category list are inaccessible via API, the team must avoid overpromising accuracy or "live" capabilities. The tool should act as a concierge that routes users to the correct official channels.

## Reconstructing Today’s Taxonomy from Public Sources — Combine rva.gov + Open311 + proxy city structures

You can credibly infer category structure by mining official service pages and mapping them into a standards-based schema.

### rva.gov service pages → the authoritative backbone

Department pages enumerate perennial services and reporting channels; use their exact language. The City of Richmond's Public Works department lists core services such as Potholes, Bulk & Brush, Graffiti, Trash, Sidewalks, Snow Removal, Leaf Collection, and Urban Forestry [2]. These pages contain vital operational rules that should populate the MVP's taxonomy. For example, Bulk and Brush collection is now a bi-weekly service that mirrors the recycling schedule, with 24-hour collection requests available for $100 and appliance collection for $50 [3]. Pothole repair efforts accelerate when winter ends and temperatures rise [2]. Crawl these pages to extract category names, descriptions, eligibility, preparation rules, and contact pathways.

### Open311 schema → a portable, future-proof shape

Use GeoReport v2’s service discovery, service_code, and metadata attributes to structure forms and validations. The Open311 API handles service discovery via a `GET Service List` method, where each service has its own `service_code` [4]. Some services require specific information (e.g., pothole depth), which is handled by the `GET Service Definition` method when the server adds `metadata="true"` to its response [4]. Create a local JSON "service catalog" utilizing this structure (service_code, service_name, group, description, required attributes) so the MVP remains portable and ready if APIs open in the future.

### Proxy taxonomy from San Francisco → 2-tier pattern to adopt

San Francisco's Category and Request Type structure is clear and current; borrow the hierarchy, not the labels. DataSF publishes 311 cases using a two-tier system: `Category` (the human readable name of the service request type, mapped to `service_name`) and `Request Type` (the human readable name of the service request subtype, mapped to `service_subtype`) [5]. Map RVA services to this 2-tier hierarchy, preserving RVA terminology from rva.gov while adding synonyms for user search.

| Proxy Taxonomy Source | Evidence/Examples | Strength for RVA | Risks | How to use in MVP |
| :--- | :--- | :--- | :--- | :--- |
| rva.gov department pages | Potholes, Bulk & Brush, Trash, Sidewalk, Graffiti [2] [3] [6] [7] | Authoritative, up to date | Fragmented pages; occasional policy changes | Extract labels, descriptions, rules; primary labels in taxonomy |
| Open311 GeoReport v2 | Service list, service_code, attributes [8] [4] | Standard, portable | Not necessarily vendor-implemented in RVA | Define schema and validation pattern for local catalog |
| DataSF 311 | Category (`service_name`), Request Type (`service_subtype`) [5] | Mature 2-tier structure | City-specific labels differ | Adopt hierarchy pattern; avoid label copying; use as structure reference |

*Takeaway: Combine the authoritative content of rva.gov with the structural rigor of Open311 and San Francisco's 2-tier hierarchy to build a robust, localized taxonomy.*

## What Historical (2014–2015) Data Still Tells Us—and What It Doesn’t

Use 2014–2015 SeeClickFix data for infrastructure patterns and seasonality; avoid extrapolating to modern program demand or exact categories.

### Still useful: infrastructure categories, seasonality, geography

Potholes, graffiti, trash, and sidewalks likely persist as core issues. Winter-to-spring pothole spikes align with rva.gov’s stated maintenance cycle [2]. Identify the top 10 infrastructure requests and hotspots from the 2014–2015 dataset to inform default shortcuts and map overlays, clearly labeling them as historical references.

### Misleading today: programmatic categories and volumes

Modern RVA311 covers finance and social programs absent from SeeClickFix data, and this program mix changes quickly. For example, in 2025, the city received 3,835 requests regarding the RVA Stay Gap Grant Program, which was temporarily paused on Jan. 16 [1]. Additionally, the Water Crisis Recovery Fund ranked in the top 10 most-recorded 311 concerns for 2025 [1]. Do not infer current program demand from 2014–2015 data; instead, manage programs via a dynamic "Programs & Alerts" panel sourced from rva.gov updates.

| Historical Data Question | Helps? | Why | Caveat/Action |
| :--- | :--- | :--- | :--- |
| What are evergreen services to feature? | Yes | Core public works persist | Validate names/rules on rva.gov |
| Where are likely hotspots? | Yes (infra) | Street assets stable | Re-validate with current community feedback |
| What are today’s top programs? | No | Post-2018 scope expanded | Curate from rva.gov news, not old data |
| Exact category labels today? | No | Taxonomy drift likely | Use rva.gov wording; avoid historic labels |

*Takeaway: Historical data is a structural guide for physical infrastructure but is dangerously outdated for social and financial city programs.*

## MVP Architecture Under Constraints — Local catalog, smart search, and guided routing

A local, standards-shaped catalog plus search and rules-based routing yields high perceived utility without live data.

### Data layer: local service catalog JSON

Structure the catalog using Open311 principles: `service_code`, group (e.g., "Public Works"), `service_name` (e.g., "Bulk & Brush"), description, required/optional attributes, department owner, channel, policy notes, fees, seasonal flags, and synonyms.

### UX flows: "Find, confirm, act"

* **Find:** Search by plain language; category browse with seasonal pins.
* **Confirm:** Show eligibility and rules (e.g., Bulk & Brush prohibited items include construction debris, carpet, auto parts, bricks [3]).
* **Act:** Route to rva311.com, phone 3-1-1, or department forms.

### Form attributes via Open311-style metadata

Standardize data capture using Open311-style metadata flags [4]. For example, a pothole report might require location, size, and a photo. This makes the tool easy to export if APIs open.

### Geospatial helpers and Content operations

Use address lookups to surface district-specific rules based on rva.gov content. Implement a weekly crawl of rva.gov pages to detect policy changes, and curate a "Programs & Alerts" section from rva.gov news, ensuring items are timeboxed with end-dates.

## Risk and Accuracy Management — Set expectations, design for safety

Accuracy comes from official content and conservative routing; transparency builds trust.

| Risk | Example | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Ephemeral programs | Water Crisis Recovery Fund (2025) [1] | Outdated guidance | Timebox programs; pull status from rva.gov news |
| Policy changes | Bulk & Brush rules updated [3] | Wrong prep steps | Weekly content checks; version stamps on pages |
| Category mismatch | "Brush pickup" vs "Yard waste" | Misrouting | Synonyms, search tuning, user feedback loop |
| Overclaiming "live data" | Demo language | Trust erosion | Standard disclaimer; route to official channels |

*Takeaway: Proactively manage the risks of static data by building in expiration dates for programs and clear disclaimers for users.*

## Demo Communication Strategy — Say what it is, and what it isn’t

Use consistent language: the tool is powered by public content, has no live access, and official requests go to rva311.com or 3-1-1.

| Topic | Do say | Don’t say | Rationale |
| :--- | :--- | :--- | :--- |
| Data source | "Based on public rva.gov content and open standards" | "Powered by RVA311 data" | No API since 2018 |
| Capability | "Routes you to the right City channel" | "Submits and tracks cases" | No submission integration |
| Accuracy | "Continuously updated from City web pages" | "Real-time 311 insights" | Avoid implying live feeds |
| Programs | "Current programs as listed on rva.gov" | "Complete 311 program list" | Programs change quickly |

*Takeaway: Honest framing of the tool as a navigation aid rather than a live dashboard will protect the team's credibility during the hackathon demo.*

## Validation Plan and Metrics — Prove usefulness without live data

Measure routing accuracy and user task completion, not case throughput. Track the percentage of rva.gov service pages captured and the percentage of test tasks that end in the correct official channel. Monitor content freshness (days since last update) and user success rates. Conduct shadow testing with 5–10 top scenarios validated by call center SMEs.

## Implementation Roadmap — 48-hour hack to 60-day pilot

**Phase 0 (Hackathon, 48–72 hours):** Build local catalog scaffolding (Open311-shaped JSON). Manually curate 15–25 services from Public Works (potholes, sidewalks, trash, bulk/brush, graffiti) with attributes and rules. Implement search, browse, and action routing. Add a "Programs & Alerts" panel with 2–3 current items from rva.gov.

**Phase 1 (Weeks 1–4):** Expand to Finance/Billing and top informational requests. Add geocoder and address-based hints. Create content diff tooling.

**Phase 2 (Weeks 5–8):** Validate with 3-1-1 SMEs; refine synonyms; add accessibility prompts. Prepare for potential API opening by ensuring the catalog is an Open311-compliant service list.

## Appendix — Source Evidence and Design References

All structures and examples are grounded in public sources:
* **rva.gov:** Public Works pages detailing Potholes, Bulk & Brush (including rules and fees), Graffiti, Trash, and Sidewalks [2] [3] [6] [7].
* **WRIC:** ~203,000 calls and ~75,200 requests created in 2024 (corrected 2026-03-18); program volumes and pauses [1].
* **Open311:** GeoReport v2 spec, Service Discovery, and metadata attributes [8] [9] [4].
* **DataSF:** "311 Cases by Category & Request Type" demonstrating a two-level taxonomy pattern [5].

## References

1. *Most common RVA 311 requests: What Richmonders needed help with in 2025 | WRIC ABC 8News*. https://www.wric.com/news/local-news/richmond/311-requests-richmond-2025/
2. *Potholes and Street Maintenance | Richmond*. https://www.rva.gov/public-works/potholes-and-street-maintenance
3. *Bulk and Brush | Richmond*. https://www.rva.gov/public-works/bulk-and-brush
4. *Open311: Explained / mySociety*. https://www.mysociety.org/2013/01/17/open311-explained/
5. *311 Cases by Category & Request Type (Jan 1, 2025 to present) | DataSF*. https://data.sfgov.org/City-Infrastructure/311-Cases-by-Category-Request-Type-Jan-1-2025-to-p/uiyx-5kqf
6. *Graffiti Removal | Richmond*. https://www.rva.gov/public-works/graffiti-removal
7. *Trash Collection | Richmond*. https://www.rva.gov/public-works/trash-collection
8. *GeoReport v2*. https://wiki.open311.org/GeoReport_v2/
9. *Service Discovery*. https://wiki.open311.org/Service_Discovery/