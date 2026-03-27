# From Open Data to Decisions: Prior Art Blueprints for a Richmond Contracts Expiry and Vendor Insights Dashboard

## Executive Summary
To accelerate the development of a Richmond contract expiry dashboard and cross-source finder, we analyzed leading municipal procurement transparency tools. The data reveals that Socrata (Tyler Technologies) serves as the de facto backbone for city open data, enabling rapid, low-code analytics through standardized OData and REST APIs. Leading cities like San Francisco and Austin rely heavily on these platforms to expose contract start and end dates, while New York City's open-source Checkbook NYC provides a mature blueprint for API filtering, version control, and sub-vendor tracking. 

For a hackathon-scale MVP, the most viable path is to fork existing open-source UI patterns (like Checkbook NYC) and connect them directly to Richmond's Socrata endpoints. By implementing automated "days-to-expiry" calculations and enriching the data with community-maintained procurement thresholds (such as Code for America's OpenProcure), the team can deliver immediate value. Crucially, the "advisory vs. authoritative" dilemma is solved not through perfect data, but through transparent UX: clear disclaimers, explicit notes on data exclusions, and deep links to authoritative procurement records.

## Purpose and Decision Frame
We will adapt successful, low-friction city approaches (Socrata + open-source UI) to ship an expiring-contracts dashboard and vendor insights module within hackathon constraints. By leveraging existing prior art from major municipalities, the Richmond team can bypass architectural guesswork and focus directly on user value: alerting buyers to upcoming expirations and providing contextual vendor insights.

## Prior Art Landscape
NYC, SF, and Austin demonstrate complementary models—custom APIs, Socrata-native datasets, and dual-channel publishing—that can be combined for Richmond.

### NYC Checkbook 2.0 Contracts API enables deep filtering and version control
Open-source code plus a rich API (status, category, vendor, award method, start/end dates) offers a reusable blueprint for Richmond's filters and data model. Launched in July 2010 by the New York City Comptroller's Office, Checkbook NYC is an open-source transparency tool that places city spending in the public domain [1]. The Contracts API requires specific parameters like `status` (registered or pending) and `category` (expense, revenue, or all) to function [1]. It supports advanced filtering, including `start_date` and `end_date` ranges, and allows users to search for both prime and sub-vendor data [1]. Notably, if no fiscal year is provided in the search criteria, the API defaults to displaying only the latest version of the contract [1]. The platform also includes a formal disclaimer and privacy policy [1].

### SF Supplier Contracts (cqi5-hm2d) exposes expiry fields with weekly updates
Term End Date + OData endpoints + weekly publishing make SF a near plug-and-play model for an expiry dashboard. The San Francisco Controller's Office maintains the Supplier Contracts dataset (Inventory ID CON-0029), which contains 47.6K rows and 21 columns [2]. Crucially for an expiry tracker, the dataset explicitly includes a `term_start_date` and a `term_end_date` (the expiration date of the contract term) [2]. The data is published weekly with a daily change frequency and is accessible via OData V2 and V4 endpoints, allowing direct connections to tools like Excel or Tableau [2]. The city notes that sensitive contracts related to certain legal proceedings are removed to balance disclosure with confidentiality [2] [3]. Furthermore, the dataset only reflects contracts awarded after July 1, 2017, when the city implemented its PeopleSoft system [2] [3].

### Austin Contracts via Socrata + Finance Online shows dual-channel delivery
A custom-facing list and a Socrata dataset provide redundancy and broader reach. Austin maintains a "Current Contract List" on its Finance Online portal, displaying categories, descriptions, authorized limits, and spent amounts [4]. Simultaneously, the city utilizes Socrata (now Tyler Technologies' Data & Insights division) for its open data portal, as evidenced by dataset 84ih-p28j [5]. Interestingly, Austin's own contract list includes a $5,000,000 master agreement for "SW-SOCRATA-CLOUD PLATFORM FOR CONNECTED GOVERNMENT DATA," highlighting the institutional reliance on this infrastructure [4].

### Comparison Table

| City/Tool | Platform | Dataset/API ID | Expiry Field(s) | Update Frequency | Sub-vendor Support | Open Source | Disclaimer/Notes |
|---|---|---|---|---|---|---|---|
| NYC Checkbook Contracts API | Custom API | N/A (API docs) | `start_date`, `end_date` filters | N/A in doc excerpt | Yes (flags for sub-vendors) | Yes (Checkbook OSS) | Formal Disclaimer; "latest version" logic [1] |
| SF Supplier Contracts | Socrata | cqi5-hm2d | `term_end_date` | Weekly publish; daily change freq | Team member fields; prime contractor | No (platform-managed) | Sensitive contracts removed; PeopleSoft cutoff [2] [3] |
| Austin Contracts | Socrata + custom site | 84ih-p28j; Finance Online list | Varies by dataset | N/A | Not specified | No (platform-managed) | City uses Socrata widely [4] [5] |

## Advisory vs Authoritative
Clear disclaimers + source links + coverage notes let cities move fast without misrepresenting authority. Checkbook NYC handles this by providing a formal disclaimer page and explicitly labeling contract statuses as either "registered" or "pending" [1]. San Francisco addresses the gap between open data and authoritative records by documenting its exclusions: the dataset removes sensitive contracts exempt from disclosure and explicitly states that contracts expired before the July 1, 2017 PeopleSoft implementation are not included [2] [3]. For Richmond, the dashboard must mirror this approach by including a visible "Data coverage and exclusions" banner, timestamping the last data refresh, and providing deep links back to the authoritative procurement office records.

## Technical Building Blocks for a Hackathon-Scale MVP
Use Socrata APIs + Checkbook-style filters + lightweight cross-source checks to deliver value in days.

### Data ingestion and normalization from Richmond's Socrata dataset
Pull only required columns (contract number/title, department, vendor, start/end dates, amount, status); cache with last-modified/ETag. Socrata's OData endpoints allow for direct, refreshable connections [2].

### Expiry detection and alerts
Compute DTE (days-to-expiry) and flag 30/60/90-day cohorts; schedule nightly refresh; UI filters by department and vendor. Utilizing fields analogous to SF's `term_end_date` [2] will drive this logic.

### Vendor insights and sub-vendor scaffolding
Mirror Checkbook's prime/sub structure even if sub-data is initially sparse; create placeholders and backlog for future ingestion. Checkbook NYC's API supports fields like `contract_includes_sub_vendors` and `sub_contract_status` [1].

### Cross-source "advisory" checks
Add advisory-only modules for vendor status and conflicts, explicitly labeled and linked to sources. This can include cross-referencing with tools like Open Procure, an online open data repository of government purchasing information across the United States [6].

## Open-Source and Reusable Components
Combine Checkbook NYC OSS, OpenProcure references, and Socrata OData to minimize net-new engineering.

### Reusable tools table

| Tool/Repo | Function | Why it matters for Richmond | Notes |
|---|---|---|---|
| Checkbook NYC (open source) | Contracts UI/API patterns | Proven filters and pagination for contracts | Requires adaptation to Richmond schema [1] |
| OpenProcure (GitHub) | Procurement thresholds reference | Contextualizes whether competition was required | Community-maintained; static data [6] [7] |
| Socrata OData/REST | Data access layer | No-code/low-code analytics; easy refresh | Built-in with Tyler Data & Insights [5] [2] |
| PDF parsing libs | Extract fields from PDFs | Backfill missing fields like term dates | Evaluate in later phase |

## Risks, Failure Cases, and Mitigations
Known gaps (pre-migration blind spots, sensitive-contract removals, required-query pitfalls) can be mitigated with UX and documentation. San Francisco's data explicitly excludes contracts that expired before 7/1/2017 or had no remaining contracting authority at that time [2] [3]. This creates a historical blind spot that would skew longitudinal analytics; Richmond must clearly mark the reliable-coverage window. Additionally, Checkbook NYC's API returns errors (e.g., Code 1000) if required parameters like `type_of_data` are missing, and enforces a 1,000 record limit [1]. The Richmond UI must implement prebuilt queries and validation guardrails to prevent users from hitting these API walls.

## The Richmond Model
Start with expiry visibility and advisory vendor context; expand to sub-vendors and advanced analytics once data matures.

### Architecture at a glance
Socrata ingestion → normalization → expiry cohorting → dashboard/API → advisory modules.

### MVP scope and acceptance criteria
Deliver searchable contract list with days-to-expiry, filters (department/vendor/status), and CSV export; document coverage and disclaimers.

### Data schema mapping and required fields
Align to fields common to SF and NYC patterns: `contract_no`, `contract_title`, `department`, `prime_contractor`, `term_start_date`, `term_end_date`, and status [1] [2].

### Roadmap to v1.1 (sub-vendors, thresholds, cross-checks)
Add prime/sub relationships, OpenProcure threshold tagging, and advisory cross-source lookups.

## Implementation Plan
Parallelize ingestion, UI, and advisory modules; ship in days, refine in weeks.
* **Week 1:** Establish Socrata data ingestion, build the core expiry logic (DTE calculation), and deploy the base UI with disclaimers and "as of" dates.
* **Week 2:** Implement vendor filters, CSV export functionality, and basic advisory checks. Write the "Data Coverage" documentation and conduct usability testing with procurement buyers.

## Appendix
Provide direct links and schemas to speed engineering.

### Datasets and APIs referenced
* **San Francisco Supplier Contracts:** Socrata dataset `cqi5-hm2d`. Includes 21 columns such as `contract_no`, `term_start_date`, and `term_end_date`. Published weekly [2].
* **Austin Contracts:** Socrata dataset `84ih-p28j` [5].
* **NYC Checkbook API:** Requires `status` and `category` parameters. Supports XML requests and responses [1].

### Sample queries and code snippets
Prebuilt OData/REST and Checkbook-style queries for expiry windows, vendor filters, and pagination.

```xml
<request> 
 <type_of_data> Contracts_OGE </type_of_data> 
 <records_from> 1 </records_from> 
 <max_records> 150 </max_records> 
 <search_criteria> 
 <criteria> <name> status </name> <type> value </type> <value> registered </value> </criteria> 
 <criteria> <name> category </name> <type> value </type> <value> expense </value> </criteria> 
 </search_criteria> 
</request>
```
*(Adapted from Checkbook NYC Sample Request [1])*

## References

1. *Contracts API | Checkbook 2.0*. http://www.checkbooknyc.com/contract-api
2. *Supplier Contracts | DataSF*. https://data.sfgov.org/City-Management-and-Ethics/Supplier-Contracts/cqi5-hm2d
3. *Supplier Contracts - Dataset - Catalog - Data.gov*. https://catalog.data.gov/dataset/supplier-contracts
4. *current contract list*. https://financeonline.austintexas.gov/afo/contract_catalog/RptCurrContractList.cfm?ccat=X
5. *Contracts | Socrata API Foundry - Data & Insights*. https://dev.socrata.com/foundry/data.austintexas.gov/84ih-p28j
6. *GitHub - munirent/openprocure: An open list of government procurement thresholds · GitHub*. https://github.com/munirent/openprocure
7. *Open Procure · GitHub*. https://github.com/openprocure