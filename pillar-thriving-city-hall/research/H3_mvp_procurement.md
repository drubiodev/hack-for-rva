# Procurement Risk Review MVP: Fastest Credible Path with Lowest Dependencies

## Executive Summary

To deliver a credible, working prototype within the hackathon time constraints, **Approach A (Contract Expiry Dashboard)** is the only viable path for the Minimum Viable Prototype (MVP). It requires no external APIs, relies solely on the readily available City Contracts CSV, and can be built in 8–12 hours. 

Approach B (PDF Contract Extractor) is currently blocked due to a lack of sample PDFs, and Approach C (Cross-Source Finder) carries high integration risks due to unverified external dependencies (SAM.gov API keys and eVA CSV availability). By focusing on Approach A, the team can guarantee a functional, advisory-only demo that calculates days-to-expiry and spend-at-risk, effectively demonstrating value without requiring a named City procurement champion.

## Constraints and Data Sources Verified

Understanding the data landscape is critical to avoiding Day 1 blockers. The current constraints dictate a highly focused approach to data ingestion.

### Socrata API and CSV are both supported

The SODA API returns all 9 columns correctly — no column bug exists (corrected 2026-03-18; prior claim of an 8-column bug was incorrect). Both the SODA API and Socrata's direct CSV export are available and reliable. Users can download datasets directly from the primer page by selecting the **Export** button and choosing the CSV format [1] [2]. The CSV format handles embedded commas and newlines by wrapping strings in quotes, and escapes internal quotes by doubling them (e.g., `""`) [3]. A robust CSV parser is required to handle these formatting rules without breaking data rows.

### VITA portal has no API (Cobblestone)

Virginia Information Technologies Agency (VITA) statewide contracts are hosted on a Cobblestone Systems web portal [4] [5]. Users can browse and search active contracts through this interface [4] [6], but there is no documented API available for automated data extraction. Consequently, VITA data must be excluded from the automated MVP scope.

### SAM.gov and eVA dependencies remain unverified

Approach C requires a free SAM.gov API key (which must be registered before the event) and an eVA CSV export. Without these confirmed in advance, relying on them introduces unacceptable schedule risk.

## Feasibility by Approach

The following table evaluates the three proposed approaches based on their dependencies, build time, and overall feasibility for the hackathon.

| Approach | Core Data | External Dependencies | Est. Build Time | Critical Blockers | Primary Risks | Feasibility Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A: Contract Expiry Dashboard** | City Contracts API or CSV (9 cols) | None; API or CSV download | 8–12 hrs | Date normalization | CSV/JSON parsing; date anomalies | **Green — MVP-ready** |
| **B: PDF Contract Extractor** | Contract PDFs | Sample PDFs (>=5 on Day 1); LLM | 10–14 hrs | 0 PDFs currently available | No data; LLM mis-extraction; advisory-only limits | **Red — Blocked** |
| **C: Cross-Source Finder** | City CSV + SAM.gov + eVA CSV | 1 SAM.gov key; eVA CSV access | 14–18 hrs | Unverified eVA CSV; key lead time | Taxonomy matching; API hiccups | **Yellow — Only if deps ready** |

*Takeaway: Approach A is the only option that guarantees a working demo within the allotted time, as it relies entirely on data we already know is accessible.*

## Approach A Deep Dive

Approach A delivers a compact feature set that showcases advisory risk insights, provenance, and polish without relying on external dependencies.

### Must-have features (deliver in 8–12 hours)

To build a credible advisory view, the MVP must include:
* **Robust CSV Ingestion:** Utilize a parser capable of handling Socrata's specific CSV formatting, including quoted fields with newlines and escaped quotes [3].
* **Date Normalization & Math:** Parse the `start_date` and `end_date` columns to compute `days_to_expiry`.
* **Interactive Filters:** Implement 30/60/90-day filters and sortable columns (department, vendor, amount).
* **Spend-at-Risk Aggregation:** Sum the `amount` field within the 30/60/90-day cohorts to provide tangible, advisory risk metrics.
* **Transparency & Provenance:** Include a details pane showing the original source row and a "How this was calculated" explainer.
* **Advisory Banner:** Prominently display "Information only — not a compliance determination" to satisfy the advisory-only constraint.

### Failure cases to handle explicitly

To build trust without a named champion, the tool must handle edge cases gracefully:
* If `start_date > end_date`, tag as "Data Issue" and exclude from aggregates.
* If `end_date` is null, bucket as "Unknown expiry".
* If `amount` is unparseable, default to 0 in aggregates and display a warning icon.

## Approach B Assessment

Approach B is currently blocked. With zero sample PDFs available, the extraction process cannot be built or demonstrated. Even if PDFs are acquired, the build time is 10–14 hours, and the LLM extraction carries risks of misreading renewal clauses or pricing terms. 
*Unblock plan:* Do not pursue unless at least 5–10 representative PDFs are secured before kickoff. If pursued later, it must remain strictly advisory with human-in-the-loop QA.

## Approach C Assessment

Approach C should only be considered as a Phase 2 enhancement. It requires joining the City CSV with SAM.gov and eVA data using keyword searches (e.g., "janitorial services") and vendor-normalization heuristics. 
*Unblock plan:* Proceed only if 1 SAM.gov key is active and the eVA CSV is pre-downloaded and profiled before the hackathon begins.

## Recommended MVP Scope

Ship Approach A. The core deliverable is a dashboard that ingests the City CSV, normalizes dates, calculates days-to-expiry, and filters by 30/60/90 days to show spend-at-risk. The demo script will be highly effective: *Load the data → filter to next 60 days → see 8 contracts → click one for details (showing provenance and calculations).*

## Critical Dependencies Checklist

Before coding begins, the following must be verified:
* [ ] City CSV direct download link is confirmed accessible.
* [ ] Column map is confirmed (start date, end date, vendor, department, amount exist within the 9 columns).
* [ ] Sample rows reviewed for date formats (e.g., ISO vs MM/DD/YYYY).
* [ ] Hosting choice decided (local static app vs lightweight server).

## Risk Register & Mitigations

* **SODA column availability:** No column bug — the API returns all 9 columns correctly (corrected 2026-03-18). Either the API or CSV may be used.
* **CSV parsing edge cases:** Socrata CSVs contain embedded commas and newlines [3]. Mitigated by using a robust, standard-compliant CSV parsing library rather than naive string splitting.
* **Data anomalies:** Mitigated by flagging invalid dates/amounts and excluding them from aggregates.
* **Credibility gap:** Mitigated by prominent advisory disclaimers and visible calculation provenance.

## Work Plan and Timeline

* **Hours 0–2:** Setup, CSV ingest, field mapping.
* **Hours 2–5:** Date normalization, days-to-expiry math, UI filters.
* **Hours 5–7:** Spend-at-risk aggregates, table UI construction.
* **Hours 7–9:** Details pane, provenance display, advisory banner.
* **Hours 9–12:** Edge-case handling, QA, demo script rehearsal, and buffer for polish.

## References

1. *Export Formats for Downloading Data – Data & Insights Client Center*. https://support.socrata.com/hc/en-us/articles/202949658-Export-Formats-for-Downloading-Data
2. *Searching and Exporting Data from Socrata*. https://www.austintexas.gov/sites/default/files/files/Development_Services/GUIDE_Socrata.pdf
3. *CSV Format - Socrata - Data & Insights*. https://dev.socrata.com/docs/formats/csv
4. *Statewide Contracts | Virginia IT Agency*. https://www.vita.virginia.gov/procurement/statewide-contracts/
5. *
	VITA - Contract Management System Public Portal
*. https://vita.cobblestonesystems.com/public/SearchResults.aspx?wc=oplYouSJ3cTDS2kwbVIpB7B9jkWJca5kFqoixwV30E72Kpa74yH7lUGDM23T14p9FztxpJgyVaIIOcxZ0uy9wA%3D%3D
6. *Procurement | Virginia IT Agency*. https://www.vita.virginia.gov/procurement/