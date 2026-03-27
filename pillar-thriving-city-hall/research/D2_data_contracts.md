# Richmond City Contracts (xqn7-jvv2) — What’s Reliable Now, What to Fix Fast for an Expiry Dashboard

## Executive Summary
The Richmond City Contracts dataset (Socrata ID: xqn7-jvv2) provides a robust, monthly-updated foundation for building a contract expiry dashboard, but it requires specific ingestion workarounds and data normalization to be reliable. The dataset contains 1,362 records spanning from 2011 to 2050, with excellent completeness in critical fields like expiration dates (0% missing). However, a known API bug silently drops the `Description` field from the SODA `/resource` endpoint, meaning developers must use the CSV download or OData endpoints to capture all 9 columns. 

For a hackathon team building an expiry tracker, the immediate priorities are bypassing the API bug, canonicalizing messy vendor names (which currently fragment spend analytics), and filtering out placeholder contract values ($0 and $1) and far-future "indefinite" expiration dates (e.g., 2050-01-01). By focusing on the two departments that drive 56% of the volume (Public Utilities and Public Works) and pre-building alerts for end-of-quarter/end-of-year expiration surges, teams can deliver immediate strategic value.

## Dataset Snapshot: 1,362 Contracts with Monthly Updates

The dataset is actively maintained and provides a comprehensive view of the city's procurement landscape. 

* **Total Records:** 1,362 contracts [1] [2].
* **Update Frequency:** The data is updated on a monthly basis [1] [2].
* **Last Updated:** March 16, 2026 [2].
* **Date Range:** The earliest contract start date (Effective From) found in the data is January 31, 2011 [3]. The latest expiration date (Effective To) extends to January 1, 2050 [1].

**Strategic Implication:** The monthly update cadence is sufficient for a 90-to-180-day expiry warning system, but the presence of 2050 end dates indicates that "open-ended" or placeholder contracts exist. These must be filtered out to avoid cluttering the dashboard with false expirations.

## Complete 9-Column Schema and API Bug Workaround

### The SODA API Bug: Missing Description Field
There is a critical discrepancy between the dataset's metadata/CSV exports and the SODA API response. While the metadata and CSV clearly define 9 columns, the SODA `/resource` API endpoint only returns 8 fields per record [2] [3]. The missing column is `Description` (API field: `description`). This was discovered by comparing the JSON keys from a sample API pull to the CSV headers, which confirmed the `description` field is entirely absent from the API output [1] [2] [3]. 

**Actionable Fix:** Do not use the SODA `/resource` endpoint for ingestion if contract context or modification notes are required. Instead, ingest directly from the CSV download URL (`/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD`) to ensure all 9 columns are captured [3].

### Schema Definition and Examples

| Display Name | API Field Name | Data Type | Example Value | Notes & Quality Issues |
| :--- | :--- | :--- | :--- | :--- |
| Agency/Department | `agency_department` | Text | Public Utilities | Includes vague entries like "City Wide" and "Not Listed" [1] [3]. |
| Contract Number | `contract_number` | Text | 20000009176 | Alphanumeric; suitable as a primary key [3]. |
| Contract Value | `contract_value` | Number | 5000000.00 | Contains placeholders like $1 (29 rows) and $0 (18 rows) [1] [3]. |
| Supplier | `supplier` | Text | Carahsoft Technology Corporation | Highly noisy; contains embedded newlines and "- INACTIVE" tags [3] [4]. |
| Procurement Type | `procurement_type` | Text | Invitation to Bid | Values include RFP, Cooperative Agreement, Agency Request [3]. |
| Description | `description` | Text | "IFB / Goods and Services..." | **Missing from API**; contains critical modification notes [2] [3]. |
| Type of Solicitation | `type_of_solicitation` | Text | Non Professional Services, Non Technology | Categorizes the nature of the work/goods [3] [5]. |
| Effective From | `effective_from` | Floating Timestamp | 11/01/2019 12:00:00 AM | 5 missing records; CSV format varies slightly [1] [3]. |
| Effective To | `effective_to` | Floating Timestamp | 05/25/2026 12:00:00 AM | 0 missing records; authoritative field for expiry tracking [1] [3]. |

*Takeaway:* The schema is well-defined, but text fields require heavy normalization. The `Contract Value` field cannot be blindly summed due to the prevalence of $0 and $1 placeholder values.

## Data Distributions: Departments, Vendors, and Solicitation Types

Understanding the shape of the data allows teams to prioritize which stakeholders to build features for first.

### Department Concentration: Two Agencies Drive the Majority

| Department | Contract Count | Share of Total (1,362) |
| :--- | :--- | :--- |
| Public Utilities | 397 | 29.1% |
| Public Works | 370 | 27.2% |
| City Wide | 122 | 9.0% |
| Information Technology | 102 | 7.5% |
| Human Resources | 44 | 3.2% |

*Takeaway:* Public Utilities and Public Works account for over 56% of all contracts [1]. An expiry dashboard should be tailored primarily to the workflows of these two departments to maximize immediate adoption.

### Solicitation Types: Non-Professional Services Dominate

| Type of Solicitation | Contract Count |
| :--- | :--- |
| Non Professional Services, Non Technology | 517 |
| Construction - Capital/Non-Capital | 182 |
| Non Professional Services, Technology | 168 |
| Supplies, Non Technology | 123 |
| Professional Services | 105 |

*Takeaway:* Different solicitation types require different renewal lead times. Construction contracts (182) will have vastly different extension protocols than Technology Services (168) [5]. The dashboard should allow users to set custom alert thresholds based on these categories.

### Vendor Fragmentation: Canonicalization is Mandatory

| Top Suppliers (Raw Data) | Contract Count |
| :--- | :--- |
| Carahsoft Technology Corporation | 24 |
| SHI INTERNATIONAL CORP | 18 |
| SIMONS CONTRACTING CO | 17 |
| CONSOLIDATED PIPE & SUPPLY | 14 |
| MESSER CONTRACTING LLC | 12 |

*Takeaway:* While Carahsoft and SHI lead the raw counts, vendor analytics are currently unreliable [4]. The data contains variations in capitalization, embedded newlines (e.g., "ENGLISH CONSTRUCTION CO\nINC"), and status tags (e.g., "ConocoPhillips Comapny - INACTIVE") [3] [4]. 

## Date Quality and Expiry Dynamics

### Expiration Dates are Complete and Clustered

The most critical field for an expiry dashboard, `Effective To`, has exceptional data quality with **0 missing records** [1]. The `Effective From` (start date) field is missing in only 5 out of 1,362 records (0.37%) [1]. 

However, expiration dates are not evenly distributed. The data shows significant clustering around end-of-quarter and end-of-year dates. For example, there are notable spikes on December 31, 2026 (20 contracts) and June 30, 2026 (18 contracts) [1]. 

**Strategic Implication:** Procurement teams will face severe capacity bottlenecks during these surge periods. The dashboard must include a "Surge Warning" feature that highlights these clusters 90 to 180 days in advance so workloads can be smoothed out.

## Data Quality Assessment and Missingness

Overall, the dataset is highly complete, but minor classification gaps exist that require graceful fallbacks in the UI.

| Field | Missing Count | Missing Percentage |
| :--- | :--- | :--- |
| Effective To | 0 | 0.00% |
| Effective From | 5 | 0.37% |
| Agency/Department | 10 | 0.73% |
| Procurement Type | 12 | 0.88% |
| Type of Solicitation | 13 | 0.95% |

*Takeaway:* Missingness in categorical fields is under 1% [1] [5]. These should be mapped to an "Unknown" or "Unclassified" bucket rather than dropping the records entirely.

## Build Plan and Cleaning Steps for a Hackathon Expiry Dashboard

To transform this raw dataset into a reliable contract expiry tracker, a hackathon team should implement the following data preparation pipeline:

### 1. Ingestion and Schema Enforcement
* **Bypass the API:** Download the data via the CSV endpoint to ensure the `Description` field is captured [3].
* **Type Casting:** Cast `contract_value` to a decimal. Treat `contract_number` as a text string to preserve formatting [1] [3].

### 2. Text Normalization (Critical Path)
* **Vendor Canonicalization:** Strip all embedded newline characters (`\n`), convert to uppercase, remove punctuation, and strip out "- INACTIVE" suffixes into a separate boolean `is_active` column [3] [4].
* **Department Mapping:** Group variations and maintain "City Wide" as a distinct, filterable category [1] [3].

### 3. Date and Value Flagging
* **Date Standardization:** Parse the CSV date strings ("MM/DD/YYYY hh:mm:ss AM/PM") into standard `YYYY-MM-DD` formats, dropping the time component as it is irrelevant for daily expiry tracking [3].
* **Far-Future Flags:** Create a boolean flag for any `Effective To` date $\ge$ 2040-01-01 (like the 2050-01-01 records) to exclude them from urgent renewal queues [1].
* **Amount Quality Flags:** Create an `amount_quality` flag. If the value is $0 or $1, tag it as "Nominal/Placeholder". Only sum values tagged as "Standard" in financial widgets [1].

### 4. Derived Metrics for the Dashboard
* **Days to Expiry:** Calculate `Effective To - Current Date`.
* **Expiry Buckets:** Group contracts into actionable timeframes: $\le$30 days, 31-60 days, 61-90 days, 91-180 days, and >180 days.
* **Surge Alerts:** Flag any month where the number of expiring contracts exceeds 150% of the rolling average.

## References

1. *Fetched web page*. https://data.richmondgov.com/api/views/xqn7-jvv2.json
2. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/d/xqn7-jvv2
3. *Fetched web page*. https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD
4. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=supplier,count(1)&$group=supplier&$order=count(1)%20desc&$limit=100
5. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=type_of_solicitation,count(1)&$group=type_of_solicitation&$order=count(1)%20desc