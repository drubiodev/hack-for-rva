# Richmond's Fastest Path to Procurement Value: A Contract Expiry Dashboard That Wins Champions

## Executive Summary

In a 48-hour hackathon environment constrained by an undocumented workflow, no pre-staged sample PDFs, and the absence of a named champion, the optimal solution is the **Contract Expiry Dashboard**. This approach leverages the only reliable asset currently available: the City Contracts Socrata CSV. 

Attempting a PDF Contract Extractor or a Cross-Source Contract Finder introduces fatal dependencies on external API keys, unverified identity matching, and unavailable ground-truth documents. By contrast, a well-executed dashboard directly aligns with what municipal procurement staff actually use daily—visibility into upcoming expirations and renewals. Furthermore, civic tech research indicates that hackathon projects are most likely to be adopted when they solve an immediate internal data visibility problem and foster relationship-building, rather than delivering overly complex, fragile prototypes. 

To succeed, the prototype must explicitly handle the "advisory only" requirement by adopting federal-style disclaimer UI patterns (e.g., "for planning purposes only") and providing direct links to source records. This strategy delivers a credible, working demo that can immediately attract a post-hackathon champion from the Procurement or Open Data offices.

## Context: Richmond's Constraints Favor a "Data-in-Hand" Solution

Richmond's current procurement risk review problem is defined by strict operational constraints that dictate technical feasibility. The project lacks a named champion to guide workflow nuances, has no pre-staged sample PDFs to train or test extraction models, and operates within an undocumented procurement workflow. 

However, the city provides a strong foundational asset: a public City Contracts dataset via Socrata containing 9 columns of structured data. In a 48-hour sprint, success depends entirely on minimizing external dependencies and maximizing the utility of this data-in-hand. Solutions that require complex data pipelines, unverified machine learning models, or cross-agency identity resolution will likely fail to produce a working demo.

## Data Landscape: Navigating SAM.gov Constraints and eVA Ambiguity

Understanding the available data sources immediately disqualifies certain approaches for a weekend prototype.

* **City Contracts (Socrata CSV):** This is the primary, frictionless data source. It is readily available, requires no authentication, and presumably contains the necessary metadata (vendor, dates, amounts) to build a functional timeline.
* **SAM.gov APIs:** While official and comprehensive, SAM.gov APIs introduce significant friction for a 48-hour build. The Entity Management API provides public data including Unique Entity Identifiers (UEI), NAICS, and PSC codes [1]. However, the Get Opportunities API restricts date range queries to a maximum of 1 year and requires pagination [2]. The Contract Awards API limits returns to 400,000 records and defaults to 10 records per page [3]. Furthermore, API key registration and approval can take time, making it a risky dependency.
* **eVA (Virginia Procurement):** While a public portal exists, clear documentation for programmatic API access or bulk data feeds is not readily available. Treating eVA as a programmatic dependency in a 48-hour window is highly likely to result in a failure mode.

## Comparative Analysis: Three Approaches Side-by-Side

To determine the optimal path, we must evaluate the three proposed approaches against the hackathon's constraints and municipal procurement needs.

| Dimension | Contract Expiry Dashboard | PDF Contract Extractor | Cross-Source Contract Finder |
| :--- | :--- | :--- | :--- |
| **Minimum Viable Data** | City Contracts CSV (all 9 columns). | 2–3 curated, high-quality contract PDFs + ground truth for verification. | City CSV + SAM.gov API (key, query logic) + eVA access. |
| **48-Hour Failure Modes** | Missing/dirty expiration dates in the CSV; weak sorting/filter UX. | OCR errors; clause misreads; no sample PDFs available to test; no QA loop [4]. | No eVA API; SAM.gov key lead time; vendor name mismatches due to lack of UEI [1]. |
| **Procurement Officer Needs** | Upcoming expirations (30/60/90 days); renewal windows; bureau/vendor filters; CSV export [5]. | Accurate extraction of expiration/renewal/pricing; confidence scores; side-by-side original text [6]. | Reliable vendor lookup across sources; unified vendor identity; relevant active awards. |
| **Advisory-Only Handling** | Banner + per-field "Advisory" badge; "Verify in source" link. | High risk if wrong—needs human review gate; advisory label not sufficient alone. | "Directionally informative" but risky without identity keys; strong disclaimers needed. |
| **Prior Art** | Tempe Procurement Contracts [5]; NYC Checkbook [7]; Portland OCDS [8]. | Vendor demos (Textract, Document AI) [9]; ibml government case studies [4]. | SAM.gov APIs widely used [10]; city-federal linking examples exist but require identity keys. |
| **Champion Likelihood** | **High**—visible, daily-use utility; easy to own post-event. | **Low**—needs data, QA pipeline, and owner to curate PDFs. | **Medium/Low**—flashy if it works, but fragile without keys/IDs. |
| **Setup Complexity** | Low | Medium/High | Medium/High |

**Takeaway:** The Contract Expiry Dashboard is the only approach where the minimum viable data is actually in hand. The other two approaches require assets (curated PDFs, API keys, unique vendor IDs) that are currently missing.

## Failure Modes and Mitigations by Approach

Only the dashboard has first-order mitigations that can be executed inside a 48-hour window.

### Contract Expiry Dashboard
* **Failure:** Missing or inconsistent expiration/renewal dates in the Socrata CSV.
 * **Mitigation:** Turn the bug into a feature. Create a "Data Health" panel that filters contracts "missing expiration" and links feedback to the data owner.
* **Failure:** Misinterpretation as compliance advice.
 * **Mitigation:** Implement strict UI disclaimers modeled after federal dashboards (detailed below).

### PDF Contract Extractor
* **Failure:** Inaccurate clause extraction and lack of sample PDFs.
 * **Mitigation:** Without pre-staged PDFs, you will test on heterogeneous scans with no ground truth. AI document analysis requires advanced NLP to understand legal context and handle complex document types [4]. If attempted, you must pre-arrange 2–3 public contract PDFs and limit scope to 3 fields with a human-in-the-loop validation UI.

### Cross-Source Finder
* **Failure:** Vendor matching errors.
 * **Mitigation:** The SAM.gov Entity API relies on UEI [1]. The City CSV likely lacks UEIs, forcing fuzzy name matches that generate false positives. If attempted, manually map 1–2 known vendors and explicitly label the feature as "experimental."

## Procurement Usability: What Drives Municipal Adoption

Municipal staff value fast, clear visibility into expirations and renewals, paired with export capabilities. 

The City of Tempe's Procurement Contracts dashboard is a prime example of prior art: it allows users to filter by "Contract Renewal End Date" and "Contract Expiration Date," filter between active and inactive contracts, and download a CSV file containing all contracts [5]. Similarly, NYC's Checkbook tool, ranked as a top transparency tool, provides intuitive dashboards with user-friendly tables and drill-down capabilities [7] [11]. 

To be useful, a procurement officer needs to see:
* **Expiry heatbands:** Contracts expiring in the next 30/60/90/180/365 days.
* **Renewal windows:** Clear cutoffs for when action must be taken.
* **Filters:** By bureau/department, vendor, and commodity.
* **Export:** CSV downloads for offline review and sharing [5].

## Advisory-Only: Patterns That Prevent Misinterpretation

Because the tool cannot make compliance determinations, "Advisory only" must be made concrete through UI patterns and governance. Federal dashboards provide excellent templates for this language.

* **Planning Purposes Only:** The Department of Justice's contracting opportunities dashboard explicitly states: "The information provided in the dashboard is for planning purposes only... Further, it is not a commitment by the DOJ" [12]. The DOT uses similar language [13].
* **Non-Endorsement and Liability:** The SBA's disclaimer notes that they assume "no legal liability for the accuracy, completeness, or usefulness of any information" [14].
* **UI Implementation:** Add an "Advisory Insight" badge on computed fields, a per-row "Verify in source" link to the original record, and a persistent footer disclaimer stating: *"For planning and advisory purposes only. Not a legal or compliance determination. Verify details in official contract documents."*

## Prior Art and Literature Synthesis: Why a Dashboard First

The procurement transparency literature strongly supports starting with basic data visibility. The Open Contracting Partnership emphasizes that "you can't manage what you can't measure," advocating for the use of standardized open data to break down information silos [15]. 

Furthermore, research on civic hackathons reveals that the most durable outcomes are not complex digital prototypes, but rather public engagement, relationship building, and internal government awareness of open data [16]. Local government staff often use hackathons to get newly released open data into use and to receive direct feedback from users to improve future data releases [17]. GovEx guidance stresses that pilots must have clear beginnings, endings, and defined success criteria, noting that projects fail when they lack the right data or stakeholders [18]. A working dashboard that highlights data gaps (like missing expiration dates) provides immediate feedback to the city, fostering the exact type of relationship-building that leads to post-hackathon adoption.

## Recommendation: Build the Contract Expiry Dashboard Now

**The Recommended Approach:** Build the Contract Expiry Dashboard. It is the only approach with high 48-hour feasibility, obvious staff value, and a credible path to securing a champion. 

It requires no external approvals, integrates neatly with open data workflows, and demonstrates immediate, visible value. Cross-source and PDF extraction both hinge on missing pieces (API keys, eVA access, curated PDFs) and carry high failure risks. Defer PDF extraction until curated samples and a review workflow are available, and reserve cross-source integration for a Phase 2 roadmap when unique vendor IDs (UEI/FEIN) are established.

## Minimum Viable Feature Set for a Credible Demo

Focus on clarity, speed, and trust. The following MVP can be shipped in 48 hours:

### Core Dashboard Features
* **Data Ingest:** Load the City Contracts CSV (all 9 columns) and display a "Last Updated" timestamp.
* **Upcoming Expirations View:** A sortable table with quick-filter buttons for contracts expiring in 30, 60, 90, 180, and 365 days.
* **Renewal Window:** A column showing renewal dates (if present), or flagging "renewal info unavailable."
* **Filters:** Dropdowns for bureau/department, vendor, and contract status.
* **Utility:** A prominent "Export to CSV" button [5] and row-level actions to "View source record."

### Trust and Data Health Features
* **Data Health Panel:** A sidebar showing the count and percentage of contracts missing expiration/renewal dates, inviting the data owner into the iteration process.
* **Advisory Framing:** A banner disclaimer at the top, "Advisory Insight" tooltips on dates, and a footer non-endorsement statement [14] [12].

### Optional Stretch Goal (Strictly Scoped)
* **Cross-Source Teaser:** For *one specific, pre-verified vendor*, pull SAM.gov Entity data (UEI/NAICS) [1] to show what a unified profile looks like. Label this heavily as "Experimental—advisory only."

## Post-Hackathon Champion and Roadmap

To turn the demo into a sustained project, you must define a named steward and a phased plan. 

**Who to engage:** Target a Procurement Office analyst (as the operational owner) and the Open Data/Socrata portal lead (as the data steward). Schedule a 30-minute demo immediately following the hackathon to co-own next steps.

**90-Day Roadmap:**
* **Phase 1 (0–30 days):** Harden the dashboard, address top data gaps identified by the Data Health panel, and document the data dictionary.
* **Phase 1.1 (30–60 days):** Add basic alerting (e.g., automated email exports for 90-day expirations) and refine usability based on staff feedback.
* **Phase 2 (60–90 days):** Establish vendor identity mapping (UEI/FEIN) to pilot a limited SAM.gov join, and evaluate eVA programmatic options.
* **Phase 3 (Future):** Introduce PDF backfill extraction with a strict human-in-the-loop review workflow.

## References

1. *SAM.gov Entity Management  API | GSA Open Technology*. https://open.gsa.gov/api/entity-api/
2. *SAM.gov Get Opportunities Public API | GSA Open Technology*. https://open.gsa.gov/api/get-opportunities-public-api/
3. *SAM.gov Contract Awards API | GSA Open Technology*. https://open.gsa.gov/api/contract-awards/
4. *Importance of AI Document Analysis for Government Contracts*. https://www.ibml.com/blog/ai-document-analysis-for-government-contracts-why-its-essential/
5. *Procurement Contracts Report Overview:*. https://gis.tempe.gov/design/Procurement%20Contracts%20Dashboard%20Guide.pdf
6. *Contract Data Extraction Benefits and a Short “How-To” Do It ...*. https://avokaado.io/stories/contract-data-extraction-with-avokaado-ai
7. *
  Annual Summary Contracts Report for the City of New York - Office of the New York City Comptroller
Mark Levine*. https://comptroller.nyc.gov/reports/annual-contracts-report/
8. *Procurement Data Dashboards | Portland.gov*. https://www.portland.gov/business-opportunities/ocds/procurement-ocds-dashboards
9. *Intelligently Extract Text & Data with OCR - Amazon Textract - Amazon Web Services*. https://aws.amazon.com/textract/
10. *SAM.gov API Documentation - Developer Guide & Tutorial (2026) | GovCon API*. https://govconapi.com/sam-gov-api-guide
11. *Contracts Application Overview | Checkbook 2.0*. http://www.checkbooknyc.com/contracts-application-overview/newwindow
12. * Office of Small and Disadvantaged Business Utilization |  Doing Business with the Department of Justice*. https://www.justice.gov/osdbu/doing-business-department-justice
13. *Procurement Opportunity Forecast | US Department of Transportation*. https://www.transportation.gov/osdbu/procurement-assistance/summary-forecast
14. *Disclaimer | U.S. Small Business Administration*. https://www.sba.gov/about-sba/open-government/about-sbagov-website/disclaimer
15. *Open Contracting Quickstart Guide*. https://www.open-contracting.org/wp-content/uploads/2021/09/OCP21-Quickstart-English.pdf
16. *Open innovation in the public sector: creating public value through civic hackathons: Public Management Review: Vol 23, No 4*. https://www.tandfonline.com/doi/abs/10.1080/14719037.2019.1695884
17. *(PDF) Civic Hackathons: New Terrain for Local Government-Citizen Interaction?*. https://www.researchgate.net/publication/304337425_Civic_Hackathons_New_Terrain_for_Local_Government-Citizen_Interaction
18. *Cities leap into action: A report from the GovAI Coalition Summit - GovEx*. https://govex.jhu.edu/blog/cities-leap-into-action-a-report-from-the-govai-coalition-summit/