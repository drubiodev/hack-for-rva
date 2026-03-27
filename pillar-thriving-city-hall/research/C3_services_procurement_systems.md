# Stitching Richmond's Contract Intelligence: A City-State-Federal Integration Playbook

## Executive Summary

Richmond's procurement staff currently navigate a fragmented landscape of city, state, and federal systems to evaluate contracts, benchmark pricing, and ensure compliance. Cross-source linkage is highly feasible but requires strategic data modeling. The Virginia IT Agency (VITA) exposes critical linkage keys like the "eVA CTR #" and SWaM designations on its public listings [1]. Meanwhile, the eVA 2024 dataset provides a massive transactional backbone with over 1.9 million records, detailing Contract Numbers, Vendor identifiers, and SWaM booleans [2]. 

For a hackathon team building a unified tool, the immediate path to value lies in a two-step matching process (Contract Number + Vendor Name) between VITA catalogs and eVA transactions. Furthermore, VITA's portal is rich with E-Rate signals that local schools and libraries can leverage immediately [1], while federal levers like GSA's Cooperative and Disaster Purchasing programs offer quick wins for emergency and IT buys [3] [4]. By stitching these sources together, Richmond can unlock spend analysis, validate piggybacking opportunities, and accelerate compliant purchasing.

## Why this matters now — Multiple systems, one mission: faster, compliant buys

Richmond staff juggle city, state, and federal systems; a unified view can speed compliant purchasing and improve pricing and equity outcomes. Currently, buyers must manually cross-reference VITA's approved IT catalogs with eVA's historical pricing data to negotiate effectively. Furthermore, leveraging federal schedules requires navigating separate GSA portals. A consolidated cross-source contract tool will reduce buying friction, ensure diversity (SWaM) compliance, and empower data-driven negotiations by surfacing the right purchasing vehicle at the exact moment of need.

## Data source landscape with access, scale, and fit

Each source serves a distinct purpose—catalogs (VITA), transactions (eVA), city visibility (Socrata)—and demands tailored ingestion strategies for a hackathon prototype.

| System | Level | Access Method | Key Public Fields | Data Currency / Volume | URL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **City Contracts (Socrata xqn7-jvv2)** | City | Socrata API (CSV/JSON) | Contract identifiers, dates, parties (to confirm) | City-published cadence | `data.richmondgov.com/Procurement/City-Contracts/xqn7-jvv2` |
| **VITA Contracts (CobbleStone)** | State | Web UI + Scrape | Contract #, Title, Supplier, End Date, SWaM, eVA CTR #, E-Rate fields | UI suggests current; no global last-updated | `vita.cobblestonesystems.com/public/` |
| **eVA Procurement Data 2024** | State | CKAN API + CSV | NIGP, Ordered Date, Unit Price, Line Totals, Vendor, SWaM flags | 1,922,754 rows (2024) | `data.virginia.gov/dataset/eva-procurement-data-2024` |
| **GSA MAS Programs** | Federal | Guidance + eLibrary | Program eligibility, SINs, ordering procedures | Policy pages, updated 2026 | `gsa.gov/buy-through-us/purchasing-programs/multiple-award-schedule` |
| **SAM.gov APIs** | Federal | API (key required) | Contract opportunities, entity validation, exclusions | Rate limits apply | `api.sam.gov` |
| **USAspending.gov** | Federal | API | Award/recipient/spend by geo | Updated nightly | `api.usaspending.gov` |

*Takeaway:* The hackathon should prioritize the VITA and eVA integrations for immediate state-level intelligence, while using GSA guidelines to flag federally approved vendors.

## City systems deep dive — Socrata is the public mirror; RAPIDS is the system of record

Use the Socrata `xqn7-jvv2` dataset as the public contract index. The hackathon team should confirm the 9-column schema via the `columns.json` endpoint and document any API column-label mismatches to establish a reliable field alias map. 

Internally, Oracle RAPIDS serves as Richmond's financial and procurement management system. The team must determine whether RAPIDS is a standard Oracle EBS/Fusion configuration or a highly customized Richmond-specific layer. Inventorying available exports and interfaces from RAPIDS will be critical for post-hackathon integration to ensure the tool reflects authoritative internal data.

## State systems deep dive — VITA contracts and eVA transactions

VITA tells you what you can buy; eVA shows what was bought, by whom, and at what price.

### VITA CobbleStone — 12+ visible columns with E-Rate and SWaM, plus attachments

The VITA Contract Management System Public Portal provides a comprehensive catalog of statewide IT contracts [5]. The search results grid exposes critical metadata, including VITA Contract Number, Contract Title, Supplier, Contract End Date, SWaM designations, and the eVA CTR 

# [1]. Crucially for local education and libraries, the portal explicitly tracks E-Rate and Emergency Connectivity Fund (ECF) eligibility, displaying the E-Rate SPIN Number, FCC 470 Number, Category 1/2 status, and Allowable Contract Date [1].

Contract detail pages provide deeper unstructured intelligence, listing Authorized Users, Instructions for Contract Use, and downloadable Files/Attachments [6] [7]. The hackathon team should build category filters (e.g., Cloud Services, Software, Telecommunications) [8] and deploy a headless scraper to harvest attachments for text-mining scope and discount schedules.

### eVA 2024 dataset — 40+ fields enable price baselines and diversity analytics

The eVA Procurement Data 2024 dataset is a massive transactional ledger containing 1,922,754 records [2]. Accessible via a CKAN API, it exposes over 40 fields that enable granular price baselines and diversity analytics [2]. Key fields include the Entity Code, NIGP 

# and Description, Item Description, Quantity Ordered, Unit Price, Line Total, and Ordered Date [2].

For vendor and equity tracking, the dataset provides the Vendor Name, eVA ID, Contract Number, and specific boolean flags for SWAM Minority, SWAM Woman, SWAM Small, and SWAM Micro Business certifications [2]. Because pulling 1.9 million rows naively will stall the application, the team must implement server-side pagination and pre-filter by Ordered Date and Entity Code to compute NIGP-by-vendor medians effectively.

## Federal levers for speed and compliance — MAS, SAM.gov, and USAspending

Federal programs can shortcut buys and ensure vendor responsibility—wire them into the workflow.

### GSA MAS for Cooperative/Disaster Purchasing — use program language and SIN filters

The GSA Multiple Award Schedule (MAS) allows state and local government buyers to access commercial products and services [9]. Through the Cooperative Purchasing program, local governments can buy IT solutions (hardware, software, mobile device management) and security/protection equipment [4]. The Disaster Purchasing program allows purchases to facilitate disaster preparedness, response, or recovery from major declared disasters or attacks [3]. 

To utilize these vehicles, buyers should follow Federal Supply Schedule ordering procedures defined in GSAR Subpart 538.71 [10] [11]. GSA recommends including specific order language confirming the intent to buy through the MAS program [3] [4]. The hackathon tool should pre-populate this RFQ/order language and tag MAS vendors in search results. Note that MAS contractors have the right to decline these orders within five days (or 24 hours for credit card orders) [11].

### SAM.gov and USAspending.gov — entity validation and award context

While full integration may fall outside the 48-hour hackathon window, the architecture should plan for SAM.gov and USAspending.gov APIs. SAM.gov will provide real-time debarment/exclusions checks and entity validation to ensure vendor responsibility. USAspending.gov will add federal award history and locality mapping to enrich vendor risk and opportunity assessments.

## Data model and linkage — from taxonomy to trusted joins

A small set of normalized dimensions unlocks cross-source analytics. Category vocabularies do not align natively: VITA uses business-friendly IT categories [8], while eVA uses standardized 5-digit NIGP codes [2]. 

| System | Vendor Key(s) | Contract Key(s) | Diversity Key(s) | Category/Commodity Key(s) |
| :--- | :--- | :--- | :--- | :--- |
| **Socrata xqn7-jvv2** | Vendor fields | City Contract # | N/A | City category |
| **VITA CobbleStone** | Supplier name | VITA Contract #, eVA CTR # | SWaM text | VITA Category |
| **eVA 2024** | Vendor Name, eVA ID | Contract Number | SWAM booleans | NIGP # / Description |
| **GSA MAS** | Contractor name, UEI | MAS contract #, SIN(s) | N/A | SIN taxonomy |

*Takeaway:* Build a translation table mapping VITA categories to NIGP buckets. Implement a confidence-scored matching engine that attempts exact matches on Contract Number/eVA CTR 

# first, falls back to deterministic Vendor ID matches, and finally uses probabilistic name/NIGP overlap. Normalize SWaM data into a unified boolean dimension table.

## Ingestion, caching, and freshness SLAs

Lightweight pipelines with smart filtering will perform under hackathon constraints and scale later. For eVA, utilize CKAN pagination with Ordered Date windowing, caching top vendors and NIGP codes with nightly increments. For VITA, deploy HTML scraping for search results and detail pages, storing the page URL and fetch timestamp since the portal lacks a global freshness indicator. For Socrata, use direct API pulls, guarding against label mismatches using `columns.json`.

## High-value user flows for procurement staff

Design for the questions buyers actually ask:
* **Find a compliant vehicle now:** Search by commodity; show city contracts, VITA statewide options, and MAS vehicles; flag E-Rate eligibility prominently.
* **Benchmark price:** Enter a SKU or NIGP code to return eVA median/percentile pricing alongside VITA price list excerpts.
* **Vendor due diligence:** Display a unified profile showing SWaM status consistency and recent eVA transaction activity.
* **Contract lifecycle:** Track end dates from city and VITA sources, generating alerts 180/90/30 days prior to expiration.

## Risks, failure cases, and mitigations

Anticipate integration and data-quality pitfalls to avoid misleading insights. Inconsistent keys (eVA CTR 

# vs. Contract Number) require multi-key matching and a human review queue. Expect address and geo gaps; the eVA dataset often lacks geolocation for P.O. Boxes [2], so the system should tag unknowns and attempt secondary geocoding for street addresses. Finally, because VITA's portal timeliness is opaque, the UI must display "as of" timestamps for scraped data while prioritizing time-anchored eVA analytics for trend reporting.

## Hackathon scope, milestones, and success metrics

Timebox for impact—deliver a working cross-source search with two killer features.

**Milestones (48–72 hours):**
* **Day 1:** Build the eVA loader with NIGP price baselines and the VITA search scraper capturing core fields.
* **Day 2:** Implement the joiner (Contract 

# / Vendor Name), E-Rate filter, SWaM normalization, and a basic UI featuring "Find a vehicle" and "Benchmark price."
* **Stretch:** Add VITA attachment text search, inline MAS program guidance, and Socrata xqn7-jvv2 ingestion.

**Success metrics:**
* 90%+ precision on Contract Number joins (sampled).
* Median search latency under 1.5s for scoped queries.
* At least 50 NIGP categories covered with price baselines.
* 10+ VITA contracts correctly flagged for E-Rate eligibility.

## Appendix — Source URLs and API endpoints

* **VITA portal:** `vita.cobblestonesystems.com/public/`
* **eVA 2024 dataset:** `data.virginia.gov/dataset/eva-procurement-data-2024`
* **Richmond City Contracts (Socrata):** `data.richmondgov.com/Procurement/City-Contracts/xqn7-jvv2`
* **GSA MAS:** `gsa.gov/buy-through-us/purchasing-programs/multiple-award-schedule`
* **SAM.gov API:** `api.sam.gov`
* **USAspending API:** `api.usaspending.gov`

## References

1. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/SearchResults.aspx?wc=oplYouSJ3cTDS2kwbVIpB7B9jkWJca5kFqoixwV30E72Kpa74yH7lUGDM23T14p9FztxpJgyVaIIOcxZ0uy9wA%3D%3D
2. *Fetched web page*. https://data.virginia.gov/api/3/action/datastore_search?resource_id=25a59527-f14a-475d-b8da-af0155015887&limit=1
3. *Learn about Disaster Purchasing | GSA*. https://www.gsa.gov/buy-through-us/purchasing-programs/programs-for-state-and-local-governments/disaster-purchasing-program
4. *Learn about Cooperative Purchasing | GSA*. https://www.gsa.gov/buy-through-us/purchasing-programs/programs-for-state-and-local-governments/cooperative-purchasing-program
5. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/
6. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/ContractDetails.aspx?cid=1876
7. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/ContractDetails.aspx?cid=1791
8. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/SearchResults.aspx
9. *Multiple Award Schedule | GSA*. https://www.gsa.gov/buy-through-us/purchasing-programs/multiple-award-schedule
10. *Ordering procedures for MAS buying | GSA*. https://www.gsa.gov/buy-through-us/purchasing-programs/multiple-award-schedule/help-with-mas-buying/ordering-procedures-for-mas-buying
11. *More info on our state and local programs | GSA*. https://www.gsa.gov/buy-through-us/purchasing-programs/programs-for-state-and-local-governments/more-about-our-programs