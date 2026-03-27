# Richmond-ready procurement data stack — SAM.gov, USAspending, eVA mapped to a cross-source comparison MVP

## Executive Summary — What to use when: a Richmond-focused procurement data playbook

For a Richmond-focused procurement cross-source comparison tool, the most effective strategy leverages three distinct data sources, each serving a specific purpose. USAspending provides the fastest path to Richmond-specific federal award spend with no authorization required, allowing queries by recipient and place of performance locations [1] [2]. SAM.gov's Exclusions and Entity APIs are essential for debarment checks and vendor eligibility, offering production-ready v4 endpoints that support bulk CSV extracts to bypass pagination limits [3]. Finally, Virginia's eVA system delivers daily purchase-order line items statewide via a published dataset and data dictionary [4]. 

By stitching these sources together using Unique Entity Identifiers (UEI), CAGE codes, and normalized vendor names and addresses, a hackathon team can build a robust Minimum Viable Product (MVP). The recommended approach is to use USAspending for federal award spend, SAM Exclusions/Entity for eligibility and identifiers, and eVA for state PO detail, designing the system for daily refreshes and pagination-safe bulk pulls.

## Source Comparison at a Glance — Access, auth, freshness, and Richmond filters

Understanding the access patterns and constraints of each source is critical for system design. USAspending requires no API key and supports rich location filters, making it ideal for immediate integration [1] [2]. SAM.gov requires an API key and favors bulk extracts due to strict pagination limits [3]. eVA provides a straightforward daily CSV download at the line-item grain [4].

| Source | Access URL(s) | Auth | Location filters supported | Update/Freshness | Notes |
|---|---|---|---|---|---|
| USAspending | `https://api.usaspending.gov/` + `/docs/endpoints` | None | recipient_locations, place_of_performance_locations (Standard Location Object: country/state/county FIPS/city/zip) | Public API; underlying feeds may lag | Rich search + autocomplete endpoints |
| SAM Exclusions | `https://api.sam.gov/entity-information/v4/exclusions` | API key (sam.gov account) | Free text q, sections/filters; address fields present in schema | Synchronous JSON; CSV extract with emailed link; 10/page; 10k cap | Debarment/eligibility flags with UEI/CAGE |
| eVA 2024 | CSV: data.virginia.gov/resource | None (open CSV) | N/A (use vendor/address columns in CSV) | "Daily - Once"; line-item rows | Data dictionary available |

These core attributes dictate the architecture: real-time API calls for USAspending, nightly batch processing for SAM Exclusions, and daily CSV ingestion for eVA.

## SAM.gov Deep-Dive — Registration, endpoints, constraints, and Richmond use

SAM.gov provides authoritative data on vendor registration and exclusions, but its APIs require careful handling of authentication and pagination limits.

### API Registration & Keys — Generate via Account Details, store securely

Accessing SAM.gov APIs requires a registered account. Registered users can request a public API key on the "Account Details" page at `sam.gov/profile/details` [3]. Users must enter their password to view the API Key information, and the key is visible immediately until the user navigates to a different page [3]. Teams should create a shared system account, generate the key, and vault it securely for staging and production environments.

### Exclusions (Debarments) v4 — Production endpoint, pagination caps, CSV extract

The Exclusions API v4 is the production endpoint for checking debarred vendors, accessible at `https://api.sam.gov/entity-information/v4/exclusions?api_key=< value >` [3]. The API returns synchronous responses with ten records per page and is capped at returning only the first 10,000 records [3]. To bypass this limit, it can serve as an Extract API by adding the `&format=csv` or `&format=json` parameter, which provides a downloadable file URL [3]. Users can also provide an `emailId` parameter to receive the download link via email [3]. Key fields include `ueiSAM`, `cageCode`, `excludingAgencyName`, and various name and address fields [3].

### Entity & Extracts — Registration lookups and bulk downloads

For broader vendor registration data, the Entity Management API allows users to request public and controlled unclassified information [5]. Similarly, the SAM Entity/Exclusions Extracts Download API facilitates bulk data retrieval [6]. Pulling periodic entity extracts is recommended to enrich eVA data and improve vendor resolution across systems.

### Contract Opportunities & Awards — Pointers and caution

While SAM.gov hosts contract opportunities and awards data, these endpoints should be considered for a phase 2 implementation. Teams should verify the latest endpoint versions and rate limits on the GSA Open Technology portal before integrating them into the MVP, preferring bulk extracts if available.

## USAspending Deep-Dive — Richmond queries, endpoints, and payload patterns

USAspending offers a highly accessible, unauthenticated API stack that is perfect for querying federal spending specific to the Richmond area.

### Location Filter Mechanics — Standard Location Object for precise scoping

USAspending utilizes a "Standard Location Object" for precise geographic filtering [2]. This object supports keys such as `country` (a 3-character code, required), `state` (a 2-character abbreviation), `county` (a 3-digit FIPS code), `city`, and `zip` [2]. For Richmond, teams should run parallel queries using both `recipient_locations` and `place_of_performance_locations` to capture both where vendors are located and where the work occurs [2].

### High-Value Endpoints for Cross-Reference

The API provides several endpoints critical for a cross-reference tool. Endpoints do not currently require any authorization [1].
* `/api/v2/search/spending_by_award/`: Advanced award search (POST).
* `/api/v2/awards/<AWARD_ID>/`: Returns details about a specific award (GET) [1].
* `/api/v2/recipient/`: Returns a list of recipients (POST) [1].
* `/api/v2/autocomplete/recipient/`: Returns recipient names and UEI based on search text (POST) [1].
* `/api/v2/autocomplete/naics/`: Returns NAICS objects matching search text (POST) [1].

### Data Freshness & Volume Handling

Because USAspending endpoints require no authorization, they are highly accessible [1]. However, teams should design for pagination and be aware that underlying agency feeds may lag. Batching queries by fiscal year and capturing "as_of" dates will help manage data volume and set user expectations regarding freshness.

## eVA (Virginia) Deep-Dive — Dataset URL, schema, and join strategy

The eVA system provides state-level procurement data, essential for comparing local and federal vendor activity.

### Current Dataset & Access — Direct CSV and dictionary

The "eVA Procurement Data 2024 - Virginia" dataset is available on the Virginia Open Data Portal [4]. It contains purchase orders for goods and services, with an update cadence listed as "Daily - Once" [4]. The dataset provides a downloadable CSV file and a separate Data Dictionary in Excel format [4].

### Schema Highlights for Cross-Source Matching

Each row in the eVA dataset represents a "purchase order line item status" [4]. Teams should utilize the data dictionary to identify canonical fields such as supplier name, supplier address, PO number, line amount, and order date to facilitate cross-source matching.

### Joining to City Contracts Data

Because eVA data may lack federal identifiers like UEI or CAGE codes, joining it to City contracts or federal data requires a robust identity resolution pipeline. Teams should attempt exact joins on UEI/CAGE when available, and fall back to fuzzy matching (e.g., Levenshtein distance) on normalized vendor names and ZIP codes, flagging low-confidence matches for manual review.

## Cross-Source Schema Mapping — Vendor, award/order, and location alignment

Harmonizing data across USAspending, SAM.gov, and eVA requires mapping disparate schemas to a unified model.

| Concept | USAspending | SAM Exclusions/Entity | eVA 2024 | Notes/Action |
|---|---|---|---|---|
| Vendor ID | UEI, DUNS (legacy), internal recipient hash | ueiSAM, cageCode | Likely supplier name/ID in CSV | Prefer UEI; fall back to name+address |
| Vendor Name | recipient_name | name/entityName | Supplier/Vendor Name | Normalize casing, punctuation, suffixes |
| Award/Order ID | award_id, piid/fain | N/A (eligibility) | po_number + line_number | Keep award vs PO separate |
| NAICS/PSC | naics, psc via endpoints | N/A | Commodity/service fields (per dictionary) | Use USAspending for NAICS flags |
| Dates | period_of_performance start/end | N/A | order_date, delivery dates | Expose as ranges |
| Amounts | obligation, current_total_value | N/A | line_amount, total_amount | Document currency assumptions |
| Location | place_of_performance, recipient_locations | Address fields; city/state/ZIP | Supplier and ship-to addresses | Store with state + county FIPS |

This mapping ensures that the comparison tool can accurately present federal awards alongside state purchase orders while maintaining clear distinctions between data grains.

## Data Quality, Freshness, and Risk — What can go wrong and how to mitigate

Several risks must be managed to ensure a reliable tool. The SAM Exclusions API is capped at 10,000 records and returns only 10 per page [3]; this must be mitigated by using the `format=csv` extract feature [3]. Identifier gaps in eVA require name/address normalization. Location ambiguity (e.g., multiple cities named Richmond) should be resolved by using the Standard Location Object with both `state` and `county` FIPS codes in USAspending [2]. Finally, because update cadences vary (eVA is daily [4], SAM Exclusions is synchronous [3]), all records should be tagged with an `as_of_date`.

## Hackathon Build Plan — 48-hour MVP to production-ready path

To deliver a functional MVP within a hackathon timeframe, the team should focus on a thin slice of functionality.

### Day 1: Data plumbing and core queries
Focus on establishing connections. Implement the USAspending `/search/spending_by_award` endpoint using `recipient_locations` and `place_of_performance_locations`. Ingest the eVA 2024 CSV and expose a basic PO list. Generate the SAM API key and successfully fetch a CSV extract from the Exclusions v4 endpoint.

### Day 2: Vendor resolution and UX
Build the identity resolution layer to link UEI/CAGE codes and perform fuzzy matching on names and ZIP codes. Develop the user interface to display a unified vendor profile showing federal awards, state POs, and debarment status. Implement retries, rate limiting, and logging for stability.

## Validation & Examples — Prove queries return Richmond data

To validate the implementation, use concrete payloads. For USAspending, send a POST request with `recipient_locations`: `[{ "country":"USA", "state":"VA", "city":"Richmond" }]` [2]. For SAM Exclusions, use the free text `q` parameter to search for "Richmond AND VA" to verify results before switching to the bulk CSV extract [3]. For eVA, filter the downloaded CSV for supplier cities containing "RICHMOND" and spot-check the results.

## Appendix A — URLs and Endpoints

* **USAspending:**
 * Endpoints index: `https://api.usaspending.gov/docs/endpoints` [1]
 * Intro/tutorial: `https://api.usaspending.gov/docs/intro-tutorial` [7]
* **SAM.gov:**
 * Exclusions API v4: `https://api.sam.gov/entity-information/v4/exclusions?api_key=` [3]
 * Entity Management API: `https://open.gsa.gov/api/entity-api/` [5]
 * Extracts API: `https://open.gsa.gov/api/sam-entity-extracts-api/` [6]
* **eVA (Virginia):**
 * 2024 Dataset: `https://data.virginia.gov/dataset/eva-procurement-data-2024` [4]

## Appendix B — Implementation Checklists

* **SAM Exclusions extract:** Request with `format=csv`, replace `REPLACE_WITH_API_KEY` in the returned URL, and poll until the file is ready [3].
* **USAspending search:** Build the filter object using `recipient_locations` and `place_of_performance_locations` [2], page through results, and store the `award_id`.
* **eVA ingest:** Fetch the daily CSV [4], validate row counts against the data dictionary, and upsert records based on PO and line numbers.

## References

1. *USAspending API*. https://api.usaspending.gov/docs/endpoints
2. *usaspending-api/usaspending_api/api_contracts/search_filters.md at master · fedspendingtransparency/usaspending-api · GitHub*. https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/search_filters.md
3. *SAM.gov Exclusions  API | GSA Open Technology*. https://open.gsa.gov/api/exclusions-api/
4. *eVA Procurement Data 2024 - Virginia - Dataset - Virginia Open Data Portal*. https://data.virginia.gov/dataset/eva-procurement-data-2024
5. *SAM.gov Entity Management  API | GSA Open Technology*. https://open.gsa.gov/api/entity-api/
6. *SAM.gov Entity/Exclusions Extracts Download APIs | GSA Open Technology*. https://open.gsa.gov/api/sam-entity-extracts-api/
7. *Introductory Tutorial Endpoints*. https://api.usaspending.gov/docs/intro-tutorial