
# Buildable Prototypes, Honest Data: What's Missing (and What to Do) for RVA's "Thriving City Hall" Hackathon

## Executive Summary
For hackathon teams building prototypes for Richmond's "A Thriving City Hall" pillar, navigating data quality is as critical as the code itself. Our investigation into the City's open data ecosystem reveals significant gaps that require immediate strategic mitigation. Most notably, post-2018 RVA311 request data is not publicly accessible, meaning teams cannot train models on current ground truth. The City Contracts dataset provides a solid foundation but suffers from unnormalized vendor names and missing industry codes, complicating cross-source analysis. Finally, rva.gov relies on generic machine translation that is explicitly flagged as insufficient for precise service terminology. To build credible prototypes, teams must transparently acknowledge these limitations, implement robust data cleaning pipelines, and design human-in-the-loop workflows rather than relying on brittle automation.

## Source Inventory and Quality Findings

### RVA311 Requests (AvePoint) - No public dataset post-2018 blocks "current" ground truth
The most significant gap for civic tech prototypes is the lack of current 311 data. The City of Richmond transitioned to an AvePoint Service Request Management System, with an active contract running through December 31, 2026 [1]. However, there is no public dataset of these requests on the Open Data Portal. 

Relying on the available 2014 to 2015 SeeClickFix data introduces severe model drift and category mismatch risks. Service delivery, departmental structures, and request taxonomies have evolved over the past decade. Teams attempting to build automated 311 routing or category helpers must treat the historical data purely as a structural reference, not as a valid training set for 2026 operations.

### City Contracts xqn7-jvv2 - Clean schema, monthly updates; edge cases can skew metrics
The City Contracts dataset (`xqn7-jvv2`) is structurally sound and updated monthly, providing 9 consistent columns via the SODA API [2]. We found no evidence of a "missing column" bug; the API reliably returns all documented fields. However, semantic noise at the edges requires careful filtering before calculating spend or active contract metrics.

| Metric | Count/Note | Impact on Prototypes |
| :--- | :--- | :--- |
| Total rows | 1,362 | Sufficient volume for trend analysis [3]. |
| End-before-start dates | 0 | High temporal logic integrity [4]. |
| End date > 2040 | 1 | Far-future placeholders (e.g., 2050) distort "active" status [5]. |
| Contract value <= 0 or null | 18 | Skews financial aggregates if not excluded [6]. |
| Distinct suppliers | 735 | High fragmentation due to unnormalized names [7]. |

Teams should implement business rules to exclude non-positive values from spend totals and treat horizons beyond 10 years as placeholders rather than true expiration dates.

### rva.gov Content - Human-readable, machine-fragile; MT disclaimers signal translation risk
Departmental pages on rva.gov contain valuable service and contact information, but they lack consistent, machine-readable structures (like JSON-LD), making automated scraping highly brittle. Furthermore, the City explicitly notes that its website uses Google Translate to provide a "generic translation" and warns that this application "does not substitute your right to obtain a professional translation provided by the City of Richmond" [8] [9] [10] [11]. Relying on auto-translated service labels for prototype taxonomies risks severe misrouting for Limited English Proficiency (LEP) users.

## Cross-Source Joining Reality

### Vendor Identity Resolution - Expect 10 to 20% manual review for top spend
Joining City Contracts with state (eVA) or federal (SAM.gov) procurement data is hindered by the lack of unique vendor identifiers (like UEI or DUNS) in the city dataset. With 735 distinct supplier strings across 1,362 contracts [7], vendor names are highly fragmented. For example, the data contains variations like "FERGUSON ENTERPRISES INC" and "Ferguson US Holdings Inc", or "Lumin8 Transportation Technologies LLC" and "Lumin8 Technologies Services LLC" [1] [12].

| Field | City Contracts (xqn7-jvv2) | eVA (state) | SAM.gov (federal) |
| :--- | :--- | :--- | :--- |
| Legal Name | Yes | Yes | Yes |
| Alternate/DBA | No | Sometimes | Sometimes |
| Unique ID | No | State Vendor ID | UEI |
| NAICS/PSC | No | Often | Yes |

### Category Alignment (NAICS) - Absent in city data; must be inferred
The `xqn7-jvv2` dataset lacks NAICS or PSC codes entirely. To perform industry-level spend analysis or compare city procurement against broader market data, teams must infer these categories using Natural Language Processing (NLP) on the contract descriptions or enrich the data by mapping vendors to their SAM.gov profiles.

## Mitigation Playbooks

### RVA311 Prototyping without Live Data
To build credible 311 prototypes without current data, teams should:
* Label any predictive models as "Historical Demonstrations" and display low-confidence warnings.
* Design human-in-the-loop triage interfaces rather than fully automated routing.
* Prepare a FOIA request or request an AvePoint sandbox export to validate categories post-hackathon.

### Contracts Analytics with Caveats
To ensure accurate procurement analytics, implement the following data pipeline steps:
* **Filters**: Drop the 18 rows with non-positive values [6] and flag the 2050 placeholder date [5].
* **Normalization**: Apply string cleaning (uppercase, strip punctuation, remove "INC/LLC") to vendor names.
* **Enrichment**: Manually review and append SAM.gov UEIs and NAICS codes for the top 50 vendors by spend to capture the majority of the financial impact accurately.

## Communicating Limitations to Judges
Transparency is a competitive advantage. Teams should explicitly state what data is missing and how they engineered around it. 

**Suggested Scripting:**
* "Because post-2018 AvePoint 311 data is not publicly available, our classifier uses historical 2014 to 2015 structures. We designed a human-in-the-loop review system to handle the inevitable category drift."
* "Our procurement dashboard excludes zero-value records and normalizes vendor names to correct fragmentation. Industry roll-ups rely on inferred NAICS codes and are labeled with confidence scores."

Success should be defined by the robustness of the application's guardrails—such as achieving high precision on top-10 vendor joins and avoiding reliance on auto-translated taxonomies—rather than the illusion of perfect data.

## Validation and Next Steps
To move from a hackathon demo to a deployable civic tool, teams must establish a concrete validation plan:
* **Within 2 weeks**: Submit a formal request for a sample export of current AvePoint 311 categories and finalize the vendor normalization lexicon.
* **Within 30 days**: Integrate the authoritative 311 categories (if provided) and replace inferred NAICS codes with verified federal data for the top 100 vendors.
* **Governance**: Maintain versioned data dictionaries and establish an issue tracker for misrouted requests or mismatched vendors.

## Appendix - Evidence Extracts
* **City Contracts (xqn7-jvv2)**: Contains 1,362 rows and 9 columns [2] [3]. Data quality checks show 0 end-before-start dates [4], 1 far-future end date [5], 18 non-positive contract values [6], and 735 distinct suppliers [7].
* **RVA311 System**: The City utilizes AvePoint Public Sector Inc for its RVA311 Service Request Management System, with a contract running through December 31, 2026 [1].
* **Language Access**: RVA.gov displays a disclaimer stating it uses Google Translate to provide a "generic translation" which does not substitute professional translation provided by the City [8] [9] [10] [11].

## References

1. *https://data.richmondgov.com/resource/xqn7-jvv2.csv*. https://data.richmondgov.com/resource/xqn7-jvv2.csv
2. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
3. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=count(*)&$where=1=1
4. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=count(*)&$where=effective_to%20%3C%20effective_from
5. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=count(*)&$where=effective_to%20%3E%20%272040-01-01T00:00:00.000%27
6. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=count(*)&$where=contract_value%20IS%20NULL%20OR%20contract_value%20%3C%3D%200
7. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=count(distinct%20supplier)%20as%20distinct_suppliers,%20count(1)%20as%20total
8. *Language Access | Richmond*. https://www.rva.gov/immigrant-engagement/language-access
9. *| Richmond*. https://www.rva.gov/
10. *Richmond City Council | Richmond*. https://www.rva.gov/richmond-city-council
11. *Information Technology | Richmond*. https://www.rva.gov/information-technology
12. *Fetched web page*. https://data.richmondgov.com/resource/xqn7-jvv2.json?$select=supplier,%20count(1)%20as%20c&$group=supplier&$order=c%20DESC&$limit=50