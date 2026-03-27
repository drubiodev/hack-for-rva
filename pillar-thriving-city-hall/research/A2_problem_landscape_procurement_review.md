# Richmond’s Contract Review Reality: Where Work Breaks and How to Fix It

## Executive Summary
Richmond City procurement staff face a highly fragmented contract review landscape that forces manual, error-prone processes. The core difficulty stems from reconciling data across disparate systems: City contracts in Socrata, state contracts in a web-only VITA portal, federal vendor data in rate-limited SAM.gov APIs, and internal financial data locked within Oracle RAPIDS. 

The stakes for getting this wrong are high. Vendor verification failures account for approximately 26% of all Single Audit findings [1]. In one instance, FEMA deobligated $805,630 due to an improperly awarded noncompetitive contract [1]. Furthermore, municipal guidance from comparable cities demonstrates that manual proof-of-check processes add measurable cycle time and error risk, requiring staff to repeatedly search, download, and print exclusion results [2]. Compounding these workflow issues are data quality headwinds, specifically Socrata schema drift and floating timestamp datatypes, which frequently break automated ingestion pipelines [3] [4]. To mitigate these risks, Richmond must transition from manual, PDF-bound checks to automated, API-driven compliance logging, while establishing data-sharing bridges with closed systems like RAPIDS and VITA.

## Problem Landscape — Fragmented sources and closed systems force manual, error-prone review
Richmond staff must reconcile City, State, Federal, and eVA data while core spend data sits inside Oracle RAPIDS, creating significant integration and evidence-capture gaps.

| Data Source | Access Method | API Availability & Limits | Data Format & Quirks | Evidence Storage Burden |
| :--- | :--- | :--- | :--- | :--- |
| **City Contracts (Socrata)** | Public Data Portal | Yes; subject to schema drift | Tabular; floating timestamps [4] | Low; data is queryable but brittle |
| **State Contracts (VITA)** | CobbleStone Public Portal | No public API documented | Web UI / PDFs | High; requires manual PDF downloads |
| **Federal (SAM.gov)** | GSA Open Technology | Yes; 10/day (public) to 1,000/day (registered) [5] [6] | JSON / API | High; requires timestamped artifacts [1] |
| **City Financials (RAPIDS)** | Oracle eBusiness Suite | Internal only (Employee Portal) [7] | Closed ERP | High; requires IT partnership for extracts |
| **Virginia eVA** | data.virginia.gov | Yes (CSV exports) | CSV | Medium; requires manual cross-referencing |

The table above illustrates the severe interoperability challenges. While SAM.gov provides APIs, they are strictly rate-limited based on account type [5]. Conversely, the VITA portal relies entirely on a web interface, and the City's RAPIDS system is restricted to an internal employee portal [7].

## Manual Burden in Comparable Municipalities — Documentation and timing checks stretch staff capacity
City standard operating procedures (SOPs) elsewhere require repeated SAM exclusion checks and printed artifacts across roles and timing gates, materially increasing cycle time and failure points.

### Dallas SOP: Search, Download, and File for Audits
The City of Dallas requires staff to perform SAM Exclusion searches for subrecipients and vendors for transactions expected to equal or exceed $25,000 [2]. Staff must search the entity name, principals, and "Doing Business As" (DBA) names, and then explicitly download and print or save the exclusion results for audit purposes [2]. 

### Colorado OSC: Step-by-Step Exclusion Searches
Similarly, the State of Colorado provides step-by-step guidance for checking the Excluded Parties List System (EPLS) via SAM.gov, underscoring the manual touchpoints required to verify that entities are not suspended or debarred [8].

### Implication for Richmond
Without automation, Richmond staff must perform multiple manual checks per contract lifecycle. This consumes significant staff-hours and increases the risk of human error, especially when cross-referencing DBAs and principals across different procurement tiers.

## Risk Landscape — What gets missed and what it costs
Debarment verification is the most frequent audit weakness. Documentation timing and identity ambiguity are common root causes, carrying real financial clawback risks.

### Debarment Checks and Audit Findings
Federal grant recipients must verify that vendors are not suspended or debarred before awarding contracts over $25,000 [1] [9]. Vendor verification failures account for approximately 26% of all Single Audit findings, making it the most common compliance issue [1]. 

### The Cost of Failure
The consequences of inadequate verification are severe. Federal agencies can disallow all costs paid to excluded vendors. In one FEMA case, an applicant improperly awarded an $805,630 noncompetitive contract, resulting in the complete deobligation of those funds [1].

### Identity Risk and False Negatives
Because SAM.gov may not have identifiers for all firm exclusion records, staff must perform additional name searches, including nicknames, abbreviations, and DBA names [1] [2]. Failing to search these variations can result in false negatives.

### Inference: Missed Renewals and Expired Contracts
*Inference:* Because key contract details (like expiration dates and renewal windows) are often buried in PDFs rather than structured database fields, missed renewals and the continued use of expired contracts are highly likely. Quantifying this risk in Richmond would require reconciling RAPIDS spend data against contract dates.

## Data Quality Headwinds — Socrata schema drift and datatypes derail automation
API field names versus display names, validation changes, and floating timestamps are known breakpoints that can corrupt expiration and renewal tracking if unmitigated.

### Failure Example: Validation Changes Break Ingestion
Cities have reported breaking changes when Socrata tightens validation rules. For example, the City of Austin experienced a pipeline failure when Socrata began enforcing a rule against publishing boolean values to a text field, and later when sending empty strings for null values [3]. 

### Known Pitfalls: API Fields and Floating Timestamps
Socrata datasets have both display names and API field names, and data synchronization tools operate strictly using API field names [10]. Furthermore, Socrata utilizes "Floating Timestamps," which represent an instant in time with millisecond precision but lack a timezone value [4]. This complicates date logic for contract expirations.

### Mitigation Actions
To build resilient automations, Richmond must build ETL processes around API field names rather than display labels, implement schema-change monitors, and coerce date fields defensively to handle floating timestamp quirks.

## System Constraints by Source — What you can and can’t automate today
Federal data can be automated within rate limits, the state portal is web-first, City Socrata is automatable but brittle, and RAPIDS requires IT partnership.

| Task / Source | City Socrata | VITA CobbleStone | SAM.gov | Oracle RAPIDS |
| :--- | :--- | :--- | :--- | :--- |
| **Search & Identify** | Yes (API) | Web Only | Yes (API) | Internal Only |
| **Extract Expirations** | Yes (Watch datatypes) | Manual (PDFs) | N/A | Internal Only |
| **Vendor Status Check** | N/A | N/A | Rate-Limited API | N/A |
| **Proof Storage** | N/A | Manual | Manual / API | Internal Only |

The matrix highlights that while SAM.gov and Socrata offer APIs, they come with strict rate limits (1,000 requests/day for registered SAM users) [5] and schema instability [3]. VITA and RAPIDS remain the largest automation blockers due to their lack of public API access.

## Primary Friction Points for Richmond Staff — Where the work really breaks
1. **Repeated Identity Checks Without a Central Log:** Staff must manually search SAM.gov for vendors, principals, and DBAs, then manually save PDFs to prove compliance [1] [2].
2. **State Portal's Lack of API:** Comparing City contracts against state VITA alternatives requires manual web scraping and PDF reading, preventing batch comparisons.
3. **Brittle Socrata Ingestion:** Tracking City contract expirations is derailed by Socrata's floating timestamps [4] and unannounced validation changes [3].
4. **Closed Financial System:** Without direct access to Oracle RAPIDS [7], procurement staff cannot easily reconcile active spend against contract terms to detect expired contracts still in use.

## Action Roadmap — 30/60/90-day plan to de-risk and accelerate
Stand up compliance automation first, then data plumbing, then analytics.

### 0–30 Days: Secure Access and Standardize
Secure a SAM.gov "system account" API key to increase rate limits to 1,000 or 10,000 requests/day [5]. Standardize a one-click export-and-file naming convention for SAM exclusion checks (e.g., `UEI_vendorname_YYYYMMDD.pdf`) to satisfy audit requirements [1].

### 31–60 Days: Build Resilient Pipelines
Build Socrata-resilient ETL pipelines that rely strictly on API field names [10] and handle floating timestamps [4]. Request scheduled read-only extracts from Oracle RAPIDS (vendor master, POs, payments) via internal IT.

### 61–90 Days: Reconcile and Alert
Batch reconcile RAPIDS spend data against Socrata contract dates. Implement automated alerting for 90/60/30-day renewal windows and dashboard compliance KPIs to track vendor verification completion rates.

## Measurement & Governance — Prove control and value
To ensure compliance and reduce audit findings, Richmond should track specific KPIs:
* **Verification Completion Rate:** Percentage of contracts ≥$25,000 with timestamped SAM.gov exclusion PDFs on file prior to award.
* **Renewal Lead-Time Adherence:** Percentage of contracts renegotiated or renewed prior to the 30-day expiration window.
* **Debarment Hits Avoided:** Number of suspended or debarred vendors flagged prior to payment issuance.

## Risks, Dependencies, and Mitigations — Anticipate “but what about…”
* **API Rate Limits:** SAM.gov restricts public users to 10 requests/day [5]. *Mitigation:* Register for a system account and implement result caching for nightly batch checks.
* **Socrata Schema Drift:** Unannounced validation changes can break data feeds [3]. *Mitigation:* Implement automated schema monitoring and defensive data coercion.
* **Internal Data Access:** RAPIDS is closed to the public [7]. *Mitigation:* Establish an MOU with the Finance/IT department for automated flat-file exports.

## Appendix — Verified Facts, Inferences, and Unknowns

### Facts (with URLs)
* SAM.gov APIs require keys; default limits are 10/day for non-role accounts and 1,000/day for registered roles/system accounts [5] [6].
* Vendor verification applies to all procurement transactions over $25,000 and all subawards [1] [9].
* Vendor verification failures account for approximately 26% of all Single Audit findings [1].
* The City of Dallas requires staff to search SAM Exclusions and download/print the results for audit purposes [2].
* Socrata datasets use API field names for data synchronization, and floating timestamps lack timezone values [4] [10].
* Socrata validation changes can cause data publishing failures [3].
* Richmond's RAPIDS system is accessed via an employee portal [7].

### Inferences (clearly labeled)
* *Inference:* The VITA portal lacks a publicly documented API comparable to GSA; integration likely requires web exports or headless browser automation.
* *Inference:* Richmond staff’s contract terms (expirations/renewals) are often embedded in PDFs, significantly increasing manual extraction effort.
* *Inference:* Missed renewals and the risk of using expired contracts grow when date fields are locked in PDFs and Socrata schemas drift.

### Unknowns (what cannot be verified publicly)
* The exact schema or column "bug" currently affecting Richmond’s Socrata `xqn7-jvv2` dataset.
* The specific data fields and export stability of eVA datasets relevant to Richmond’s procurement categories.
* Current internal Richmond SOPs for debarment checks and historical internal audit findings regarding missed renewals.

## References

1. *Vendor Verification & SAM.gov Compliance Guide | ProcurementExpress | ProcurementExpress*. https://www2.procurementexpress.com/resources/vendor-verification-sam-gov/
2. *Recent Changes to Federal System for Award ...*. https://dallascityhall.com/departments/budget/communitydevelopment/DCH%20Documents/RecentChangesToSAM-2021.pdf
3. *Socrata Pub Fails with "Illegal field name" Error · Issue #223 · cityofaustin/atd-data-publishing*. https://github.com/cityofaustin/atd-data-publishing/issues/223
4. *Floating Timestamp Datatype | Socrata - Data & Insights*. https://dev.socrata.com/docs/datatypes/floating_timestamp
5. *SAM.gov Entity Management  API | GSA Open Technology*. https://open.gsa.gov/api/entity-api/
6. *SAM.gov API Documentation - Developer Guide & Tutorial (2026) | GovCon API*. https://govconapi.com/sam-gov-api-guide
7. *Finance | Richmond*. https://www.rva.gov/finance
8. *Checking SAM.gov for Suspension and Debarment*. https://osc.colorado.gov/sites/osc/files/documents/Checking%20SAM.gov%20for%20Suspension%20and%20Debarment%2012_2024%20%282%29.pdf
9. *Federal Compliance Requirements, Part IX – Procurement and Suspension and Debarment - Ketel Thorstenson - CPA | Advisors*. https://www.ktllp.cpa/federal-compliance-requirements-part-ix-procurement-and-suspension-and-debarment/
10. *FAQ / Common Problems | Socrata*. https://socrata.github.io/datasync/resources/faq-common-problems.html