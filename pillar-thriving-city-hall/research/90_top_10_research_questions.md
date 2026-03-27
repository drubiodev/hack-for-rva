
# Build-Ready Plan for a Thriving City Hall: Data, Dependencies, and Guardrails for Richmond's Service Navigation

## Executive Summary
For the Richmond Civic Hackathon team building under the "A Thriving City Hall" pillar, success depends on navigating Richmond's specific data structures and strict compliance guardrails. RVA311 handles over 83,000 requests annually across more than 30 departments [1], requiring a robust and adaptable taxonomy. Furthermore, Richmond's Language Access Plan (LAP) strictly prohibits the use of automated internet translation for service delivery [2], meaning any chatbot or navigation tool must prioritize human-translated vital flows and warm handoffs to live interpreters. 

While the City Contracts Socrata dataset offers a clean 9-column schema for immediate transparency wins [3], developers must account for Socrata API bugs that silently drop null fields [4]. Several critical dependencies—including the RVA311 public API, rva.gov sitemap structure, and federal/state procurement API access—directly impact hackathon feasibility and must be treated as immediate go/no-go gates for automation features.

## Hackathon Feasibility Gates & Top 10 Research Questions

Below are the answers to the 10 key questions, marked by verification status and flagged for hackathon feasibility impact.

### 1. RVA311 Request Types and Department Mappings
**Status:** Partially Verified / Inference
**URL:** https://www.rva.gov/citizen-service-and-response/about-rva-311
**Answer:** A single, exhaustive public list of all 50+ request types is not documented in one static location. However, RVA311 partners with over 30 different departments [1]. The taxonomy is dynamic; for example, in 2019, the city split "Parking Application" into "Request Handicap Parking Sign" and "Request Residential Parking Permit" to improve routing [5]. 

| Department Category | Example Request Types / Services |
| :--- | :--- |
| Public Works | Solid Waste, Bulk and Brush, Potholes, Sidewalks, Streetlights [1] |
| Public Utilities | Storm Water, Waste Water [1] |
| Social Services | Benefit Application, Child Protective Services, Homeless Services [1] |
| Finance and Revenue | Personal/Business Property Taxes, Business Licensing [1] |
| Planning and Development | Zoning and Permitting, Code Enforcement [1] |

### 2. rva.gov Sitemap Structure and Structured Data
**Status:** Not publicly documented
**URL:** N/A
**Answer:** Automated tools (searching for `sitemap.xml`, `robots.txt` references, or JSON-LD schema) do not return a public sitemap or structured-data markup for the rva.gov domain as of 2026-03-24. 
**Feasibility Flag:** **CRITICAL**. Without a verified sitemap or JSON-LD schema (BreadcrumbList, FAQ, Organization), building an automated search index or RAG (Retrieval-Augmented Generation) pipeline for city services will require manual scraping, severely limiting the scope of a hackathon project.

### 3. City Contracts Socrata Dataset (xqn7-jvv2) Columns and API Bug
**Status:** Verified
**URL:** https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
**Answer:** The dataset contains exactly 9 columns: `Agency/Department`, `Contract Number`, `Contract Value`, `Supplier`, `Procurement Type`, `Description`, `Type of Solicitation`, `Effective From`, and `Effective To` [3]. 
**The API Bug:** The Socrata API (SODA) skips empty or null fields entirely in its JSON response rather than returning an empty string [4]. This results in arrays/rows with missing keys, causing shorter rows that break naive table visualizations or data ingestion pipelines [4] [6].

### 4. SAM.gov API Registration and Rate Limits
**Status:** Verified
**URL:** https://open.gsa.gov/api/PSC-Public-API/
**Answer:** Users can obtain a personal API key from their profile page on SAM.gov [9]. Rate limits for non-federal users are 10 requests/day (public) or 1,000/day if the user has a registered role [8]. Federal users receive 1,000/day (public) or 10,000/day for system accounts [8].
**Feasibility Flag:** **MODERATE**. Affects the ability to enrich local contract data with federal data. Teams should plan a fallback to static CSV exports if API keys cannot be provisioned during the hackathon.

### 5. eVA Virginia Procurement CSV Dataset
**Status:** Verified
**URL:** https://eva.virginia.gov/eva-open-data.html
**Answer:** The Virginia Open Data portal provides downloadable CSV files for eVA procurement [10]. The latest dataset (2024) was published on 2023-07-03 and is updated daily [11]. Users must create a portal login to request and download the CSV.
**Feasibility Flag:** **MODERATE**. Affects state-level contract enrichment.

### 6. Comparable City 311 Taxonomies
**Status:** Verified
**URL:** N/A
**Answer:** Comparable cities offer robust 311 data structures: Boston groups requests by Service Category via CKAN [12]; NYC uses a large-scale OpenData table with ~200 complaint types [13]; Chicago provides a dedicated "Request Types" view listing distinct names and short codes [14]; and San Francisco aligns with the Open311 standard via DataSF [15]. Richmond's own evolution shows a move toward plain-language, highly specific intents (e.g., separating "Public Litter" from "Storm Debris") [5], mirroring the granularity seen in these benchmark cities.

### 7. Failure Modes of Government Service Chatbots
**Status:** Inference
**URL:** https://rva.gov/sites/default/files/2022-05/LANGUAGE%20ACCESS%20PLAN%20FINAL-%20APR2020.pdf
**Answer:** The primary documented failure mode in Richmond's context is language misrouting. Richmond's Language Access Plan explicitly states: "Automated internet interpretation services will not be used even in emergency situations" [2]. A chatbot that relies on automated translation (like Google Translate) to route non-English service requests violates city policy and erodes trust with the 6,537 Spanish-speaking Limited English Proficiency (LEP) residents [2].

### 8. AvePoint Citizen Services Platform API
**Status:** Not publicly documented
**URL:** https://learn.avepoint.com/docs/Overview.html
**Answer:** AvePoint publishes a Graph API that enables data-management operations [16], but the documentation does not list an endpoint for creating or updating RVA311 tickets. The product brochure confirms that AvePoint E311 "allows agencies to automate case management," yet no public API specification is provided [17].
**Feasibility Flag:** **CRITICAL**. If the AvePoint platform powering RVA311 lacks a public API for programmatic ticket creation, the hackathon team cannot build an end-to-end automated submission tool. The project must pivot to an "advisory" tool that guides residents to the correct official form or phone number.

### 9. Contract Transparency Tools on Socrata
**Status:** Verified
**URL:** https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
**Answer:** Richmond already hosts a Procurement Transparency Dashboard (linked from the City Contracts dataset page) [3], which filters by `Supplier`, `Agency/Department`, and `Contract Value`. While specific external examples were not retrieved, Richmond's 9-column schema [3] is sufficient to build a localized MVP dashboard.

### 10. Digital Equity and Accessibility Considerations
**Status:** Verified
**URL:** https://www.rva.gov/immigrant-engagement/language-access
**Answer:** Language access is a strict legal and operational mandate in Richmond. The city provides free interpretation and translation services [7]. 
* **Language:** Spanish makes up more than 96 percent of the calls to the language line [2]. 
* **Policy:** The city uses only qualified adults as interpreters and forbids the use of children under 18 [2]. 
* **Digital Guardrails:** RVA.gov features a disclaimer that Google Translate is not a substitute for professional translation provided under the LAP, directing residents to call 804-646-7000 or 3-1-1 for actual service [7]. Hackathon tools must include prominent, plain-language pathways to these phone numbers rather than relying solely on digital text.

## References

1. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
2. *1 Revised Version April 2020 LANGUAGE ACCESS PLAN...*. https://rva.gov/sites/default/files/2022-05/LANGUAGE%20ACCESS%20PLAN%20FINAL-%20APR2020.pdf
3. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
4. *Socrata API - How to replace empty data fields from query as empty strings in results array - Stack Overflow*. https://stackoverflow.com/questions/53235100/socrata-api-how-to-replace-empty-data-fields-from-query-as-empty-strings-in-re
5. *Improvements to RVA311 Request System, November 2019 | Richmond*. https://rva.gov/press-releases-and-announcements/news/improvements-rva311-request-system-november-2019
6. *Socrata API missing fields - Stack Overflow*. https://stackoverflow.com/questions/37419673/socrata-api-missing-fields
7. *Language Access | Richmond*. https://www.rva.gov/immigrant-engagement/language-access
8. *SAM.gov PSC Public API | GSA Open Technology*. https://open.gsa.gov/api/PSC-Public-API/
9. *System Account User Guide*. https://dodprocurementtoolbox.com/uploads/System_Account_User_Guide_v2_with_non_federal_access_82572248c0.pdf
10. *eVA Open Data*. https://eva.virginia.gov/eva-open-data.html
11. *eVA Procurement Data 2024 - Virginia - Dataset*. https://data.virginia.gov/dataset/eva-procurement-data-2024
12. *Boston 311 | Boston.gov*. https://www.boston.gov/departments/boston-311
13. *311 Service Requests from 2020 to Present | NYC Open Data*. https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9
14. *311 Service Requests - Request Types | City of Chicago*. https://data.cityofchicago.org/Service-Requests/311-Service-Requests-Request-Types/dgc7-2pdf
15. *311 Cases | DataSF*. https://data.sfgov.org/City-Infrastructure/311-Cases/vw6y-z8j6
16. *Overview - AvePoint Graph API Documentation*. https://learn.avepoint.com/docs/Overview.html
17. *AvePoint E311-Citizen Services Product brochure*. https://cdn.avepoint.com/pdfs/en/AvePoint_E311_Citizen_Services_for_Microsoft_CityNext_Product_brochure.pdf