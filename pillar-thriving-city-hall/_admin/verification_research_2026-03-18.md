# Verification Research Results

Pillar: Thriving City Hall (government service delivery, RVA311, procurement, Richmond, VA)
Date: 2026-03-18
Parallel.ai run_id: trun_3cad0ebea15c480e910ea5fa22a1ba8c
Processor: pro

---

# RVA Civic Tech: De-risking City Hall Integrations Before Hackathon Day

## Executive Summary

Preparing for the Richmond, VA civic hackathon requires navigating several undocumented constraints and data realities within the city's digital infrastructure. Our verification of the top 10 factual claims reveals critical pivots teams must make to ensure their demos function reliably. 

Most notably, **rva.gov lacks a sitemap and a JSON search API**, forcing teams to build custom crawlers and indexing solutions. The **RVA311 platform (AvePoint) does not expose a public API** [1] [2], meaning live service request integrations are unfeasible; teams should instead leverage historical SeeClickFix data spanning January 2014 to August 2015 for modeling [3] [4]. Furthermore, widely circulated 2025 RVA311 volume metrics (208,216 requests) are unsubstantiated; teams must anchor their KPIs to the official 2024 baseline of **203,000 calls and 75,200 created requests** [5]. 

For procurement challenges, the City Contracts dataset is fully functional via SODA API with all 9 columns intact [6], but cross-referencing with federal data will hit severe bottlenecks: **SAM.gov limits non-federal users without a registered role to just 10 API requests per day** [7]. Finally, teams should design their solutions with continuity in mind by framing **Pete Breil, Director of Citizen Service & Response**, as the primary executive champion [8] [5].

## City Web Plumbing Constraints

### No Sitemap and HTML-Only Search Enforces Custom Indexing
With no sitemap and no JSON search, teams must own discovery and indexing. The `rva.gov/sitemap.xml` endpoint returns an HTTP 404 error, and the `robots.txt` file does not list any sitemap directives. Furthermore, the search functionality operates strictly via HTML responses using zero-based pagination (e.g., `/?search={query}&page=0`), and the rumored `business_unit` facet parameters are neither present in the markup nor functional.

Discovery and recall will depend entirely on your crawler and indexer, not native endpoints. Teams must build a polite crawler seeded from the `rva.gov` top navigation and department hubs, throttling requests to avoid overwhelming the server. Pre-index this content into a lightweight search engine (like SQLite FTS or Meilisearch). To build a department taxonomy, cross-validate the inferred page structure with the official FOIA contact list [9].

## 311 Data Reality

### Closed Platform, Reliable 2024 Metrics, and Historical Samples
Treat the current RVA311 platform (AvePoint) as closed. The AvePoint Citizen Services product page returns a 404 error [1], and the official case study detailing Richmond's implementation mentions Microsoft BizTalk and Dynamics 365 integrations but lacks any reference to a public API [2]. 

Live integration risk is exceptionally high, and KPI credibility hinges on using cited metrics. The claim of 208,216 requests in 2025 is unsupported. Instead, use the official 2024 figures presented to the City Council: **203,000 calls received, 75,200 requests created, and 75,800 requests closed** [5]. For modeling categories and SLAs, utilize the historical SeeClickFix dataset (`vgg4-hjn8`), which contains ~43.3K rows spanning from January 1, 2014, to August 25, 2015 [3] [4]. Engage Director Pete Breil for any pilot access or post-event data-sharing discussions [8] [5].

## Procurement Data Integration

### SODA, CKAN, and SAM.gov Rate Limits
Procurement data spans multiple platforms with vastly different access patterns. The Richmond City Contracts dataset (`xqn7-jvv2`) is fully accessible via the Socrata SODA API and CSV downloads, consistently returning 1,362 rows and 9 columns [6]. Conversely, the state-level eVA 2024 procurement dataset is a massive ~1.1 GB CSV hosted on a CKAN portal [10]. Federal cross-referencing via the SAM.gov Entity API introduces severe rate limits: non-federal users without a role are capped at 10 requests per day, while those with a role get 1,000 per day [7].

Each source has different constraints; avoiding runtime surprises is critical for a successful hackathon demo.

### Data Source Comparison for Procurement

| Source | API/Access | Auth/Keys | Rate Limits | Size | Format |
|---|---|---|---|---|---|
| **Richmond City Contracts** (`xqn7-jvv2`) | Socrata SODA + CSV | Optional app token | Not a bottleneck | ~1,362 rows | JSON/CSV |
| **eVA Procurement 2024** | CKAN CSV download | None for CSV | N/A for static file | ~1.1 GB | CSV |
| **SAM.gov Entity API** | REST | Personal key from SAM | 10/day (no role), 1,000/day (with role) | N/A | JSON |

*Takeaway: Build a contracts crosswalk by normalizing supplier names offline. Pre-download the massive eVA datasets and convert them to Parquet for speed. Crucially, resolve suppliers to SAM.gov entities offline and cache the results to survive the 10-request daily limit.*

## Stakeholder Enablement

### Director Breil as Sponsor for Continuity
Engaging the right stakeholders early unblocks data and process questions. Pete Breil is the Director of Citizen Service & Response [8]. He recently presented the RVA311 update to the Governmental Operations Standing Committee [11] [5] and is listed as the official FOIA contact for his department [9]. Teams should request a brief sync with him to validate problem framing and secure a commitment for post-hackathon pilot access.

## Risk Register and Mitigations

Plan around these predictable pitfalls to protect demo credibility:
* **No sitemap:** Pre-crawl and cache pages; do not crawl live during the demo.
* **HTML-only search:** Use your own index; avoid live scraping in loops.
* **Unsourced 2025 metrics:** Anchor to 2024 figures with citations [5]; label calls vs. requests clearly.
* **SAM.gov 10/day limit:** Register accounts immediately to seek roles [7]; precompute and cache lookups.
* **Dataset date range mismatch:** Query `min(createddate)` and `max(createddate)` to prove the 2014-2015 range [4].

## Hackathon Implementation Playbook

Prefetch, cache, and cite to ensure stable, defensible outcomes.
* **Day -7 to -3:** Register for SAM.gov and obtain roles. Download the 1.1 GB eVA CSV [10]. Ingest City Contracts via SODA [6].
* **Day -2:** Crawl and index `rva.gov` content. Build a department taxonomy from the FOIA list [9] and site menus.
* **Day -1:** Run entity resolution for suppliers against SAM.gov with aggressive caching.
* **Day 0:** Freeze datasets. Use environment variables for API keys and ensure an offline mode is active.
* **Demo:** Display sources next to KPIs, include "Last updated" timestamps, and transparently state known caveats.

---

## Verification Items — Evidence-Backed Log Updates

### 1. rva.gov sitemap availability (E-016)
* **Verification Status:** INCORRECT
* **Official Source URL:** https://www.rva.gov/sitemap.xml (Returns 404)
* **Key Details for Teams:** No sitemap exists. Teams must build a lightweight crawler starting from `rva.gov` and main department hubs, following internal links. Respect `robots.txt` and throttle requests.
* **Corrections:** The claim that a sitemap can be used for discovery is false.

### 2. Drupal Search API facet parameters (E-006)
* **Verification Status:** PARTIALLY INCORRECT
* **Official Source URL:** https://www.rva.gov/?search=permits
* **Key Details for Teams:** The response is HTML only; no JSON endpoint is exposed. Pagination is zero-based (`page=0`). Parse the HTML or build your own index.
* **Corrections:** The `f[0]=business_unit:{id}` facet parameter is not visible in the HTML and appears non-functional. Search integration via JSON is not possible.

### 3. RVA311 2025 volume (208,216 requests) (E-004)
* **Verification Status:** LIKELY INCORRECT
* **Official Source URL:** https://richmondva.legistar.com/View.ashx?GUID=C050E3F8-7CC4-4663-BA8F-362608460B56&ID=13777233&M=F [5]
* **Key Details for Teams:** Distinguish between calls and service requests. If modeling workloads, cite the 2024 figures and note that "requests closed" can include prior-year opens.
* **Corrections:** Remove the 208,216 figure. Use the official 2024 figures: 203,000 calls received, 75,200 requests created, and 75,800 requests closed [5].

### 4. City Contracts dataset column bug confirmation (E-008, E-009)
* **Verification Status:** INCORRECT
* **Official Source URL:** https://data.richmondgov.com/Procurement/City-Contracts/xqn7-jvv2 [6]
* **Key Details for Teams:** The dataset contains ~1,362 rows. API rate limits are unlikely to be a bottleneck. Timestamps are floating timestamps.
* **Corrections:** There is no bug. Both the SODA API and the CSV download return the exact same 9 columns [6]. Teams do not need a CSV workaround.

### 5. SAM.gov API free key availability and rate limits (E-014)
* **Verification Status:** CONFIRMED (with caveats)
* **Official Source URL:** https://open.gsa.gov/api/entity-api/ [7]
* **Key Details for Teams:** API keys are free, but rate limits are severe. Non-federal users without a role get 10 requests/day. Non-federal users with a role get 1,000 requests/day [7]. Register early, cache responses locally, and avoid live bulk calls.
* **Corrections:** None, but the constraints must be heavily emphasized.

### 6. AvePoint Citizen Services platform — no public API confirmation (E-002)
* **Verification Status:** CANNOT VERIFY (Treat as no public API)
* **Official Source URL:** https://www.avepoint.com/case-studies/rva311 [2]
* **Key Details for Teams:** Assume no public API is available for service requests. The platform uses Microsoft BizTalk and Dynamics 365 [2].
* **Corrections:** The product page returns a 404 [1], and the case study lacks API documentation [2].

### 7. rva.gov department slug list (E-017)
* **Verification Status:** CANNOT VERIFY
* **Official Source URL:** https://www.rva.gov/FOIA [9] (Alternative source for taxonomy)
* **Key Details for Teams:** Build your own department index by crawling department pages and cross-referencing the FOIA contact list for official department names [9].
* **Corrections:** The claim of 40+ department slugs accessible via the `business_unit` facet is unsubstantiated.

### 8. Historical RVA311 Socrata data date range (E-001)
* **Verification Status:** CONFIRMED (with nuance)
* **Official Source URL:** https://data.richmondgov.com/d/vgg4-hjn8 [3]
* **Key Details for Teams:** The dataset contains ~43.3K rows and 19 columns [3]. Use this as a historical sample only; it is not indicative of current categories or volumes.
* **Corrections:** The actual data range is January 1, 2014, to August 25, 2015 [4]. You must use the field name `createddate` in queries; `created_at` will return a 400 error.

### 9. eVA Virginia procurement dataset URL on data.virginia.gov (E-018)
* **Verification Status:** CONFIRMED
* **Official Source URL:** https://data.virginia.gov/dataset/570f4ddb-7dca-4e2f-a329-ffad0e295e7a [10]
* **Key Details for Teams:** The platform is CKAN. The 2024 dataset is a ~1.1 GB CSV [10]. Plan for streaming or columnar conversion (e.g., Parquet). A data dictionary is provided on the dataset page.
* **Corrections:** None.

### 10. Pete Briel as Director of 311 / formal champion status (E-011)
* **Verification Status:** CONFIRMED (with spelling correction)
* **Official Source URL:** https://www.rva.gov/citizen-service-and-response [8]
* **Key Details for Teams:** His title is Director of Citizen Service & Response [8]. His email is `peter.breil@rva.gov` [5]. Identify him as the post-hackathon sponsor for data access and sustainment.
* **Corrections:** The correct spelling is **Pete Breil**, not Briel [8] [5].

## References

1. *Page Not Found - 404 | AvePoint*. https://www.avepoint.com/products/citizen-services
2. *RVA 311 | AvePoint*. https://www.avepoint.com/case-studies/rva311
3. *SeeClickFix Sample Data Aug 2014 to Aug 2015 | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/d/vgg4-hjn8
4. *Fetched web page*. https://data.richmondgov.com/resource/vgg4-hjn8.json?$select=min(createddate),max(createddate)
5. *Fetched web page*. https://richmondva.legistar.com/View.ashx?GUID=C050E3F8-7CC4-4663-BA8F-362608460B56&ID=13777233&M=F
6. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Procurement/City-Contracts/xqn7-jvv2
7. *SAM.gov Entity Management  API | GSA Open Technology*. https://open.gsa.gov/api/entity-api/
8. *Citizen Service and Response | Richmond*. https://www.rva.gov/citizen-service-and-response
9. *Virginia Freedom of Information Act (FOIA)*. https://www.rva.gov/FOIA
10. *eVA Procurement Data 2024 - Virginia - Dataset - Virginia Open Data Portal*. https://data.virginia.gov/dataset/570f4ddb-7dca-4e2f-a329-ffad0e295e7a
11. *Draft Meeting Minutes Governmental Operations Standing ...*. https://richmondva.legistar.com/gateway.aspx?M=F&ID=3cb995b8-9c46-4e3d-8cee-ce6ec48de21c.pdf