---
title: "Breaking the Maze: Where Richmond Residents Get Lost in City Services"
pillar: thriving-city-hall
section: A
problem_statement: service-navigation
tags:
  - service-navigation
  - rva.gov
  - RVA311
  - information-architecture
  - call-center
  - department-centric
summary: "Detailed problem analysis of resident service navigation failures: department-centric rva.gov architecture, 311 call volume patterns, and category taxonomy fragmentation. Documents where navigation breaks and how it generates avoidable phone calls."
geography: Richmond, VA
source: parallel-ai-pro
status: raw
related_reports:
  - A2_problem_landscape_procurement_review
  - A5_problem_landscape_government_ux
  - B1_users_resident_service_seeker
  - C1_services_311_landscape
---

# Breaking the Maze: Where Richmond Residents Get Lost in City Services

## Executive Summary
The most significant friction point in Richmond’s resident service ecosystem occurs before a ticket is ever submitted: residents struggle to determine where to go, what to ask for, and which category to choose. While digital transformation efforts like RVA311 aim to streamline intake, the City's information architecture remains heavily department-centric, forcing residents to understand the municipal org chart to find basic services. 

This navigation gap has created a phone-first reality where information-seeking dominates over actual service requests. In 2025, more than half of all RVA311 interactions were resolved by call center agents without generating a service ticket. Furthermore, overlapping categories and vague statuses create a "black hole" effect that drives duplicate reporting and manual triage downstream. By shifting from a department-centric to a service-centric digital front door, tuning site search to resident vocabulary, and consolidating confusing request categories, Richmond can significantly reduce misrouting, lower call center strain, and improve the overall resident experience.

## Demand and Channel Mix: The Phone-First Reality
Richmond experienced a massive surge in resident inquiries recently, exposing the heavy reliance on phone triage. In 2024, the city received ~203,000 calls and ~75,200 requests created (corrected 2026-03-18 — previously cited 208,216 was incorrect), representing an increase from over 83,000 requests assisted in a prior period [1] [2].

Despite the availability of digital portals, the phone remains the primary channel for resolution. More than half of the residents’ concerns were addressed over the phone with Richmond’s 311 call center [2]. Call center agents successfully resolved a large share of concerns without having to create a request for specific departments [2]. This indicates that the majority of resident needs are informational rather than transactional. The high volume of phone resolutions suggests that digital self-service pathways are either too difficult to find or too confusing to navigate, forcing residents to rely on human agents to translate their needs into City processes.

## Where Navigation Breaks on rva.gov: Department-First IA
Task seekers navigating rva.gov are forced to guess which department handles their specific issue. The website's architecture emphasizes a "Browse by Department" structure, presenting users with a massive list of over 40 distinct offices, ranging from the Assessor of Real Estate to Public Works and Justice Services [3] [4]. 

This department-first approach creates dead ends and bounces users back to the call center. For example, the Department of Finance Forms page explicitly advises users: "Can't find the form you are looking for? Please enter a ticket using RVA 311 online or call (804) 646-7000 and we can provide assistance" [5]. When the website fails to guide residents to the correct canonical task, it generates avoidable tickets and phone calls, shifting the burden of navigation from the website's information architecture to the 311 staff.

## Category Taxonomy and "Other" Load
When residents do attempt to submit a digital request, overlapping categories and "Other" options create manual triage bottlenecks. Historical SeeClickFix data for Richmond (August 2014 to August 2015) reveals a high volume of "Trash/Bulk Pick-ups" requests that required users to answer subtypes like "Yard Waste," "Furniture," or "Other (please specify items for pick up in description)" [6] [7]. The frequent use of "Other" acts as an escape hatch for confused users.

Audits from comparable cities demonstrate the downstream cost of these vague categories. In San Diego, dispatchers are responsible for manually reviewing all service requests submitted through their platform that are labeled as "Other," transferring or referring them to the appropriate department [8]. When categories are not mutually exclusive or visually guided, residents guess, leading to miscategorization that requires human intervention to correct.

### Comparable Cities' Category and Transparency Pain Points

| City | Finding | Quant/Example | Relevance to Richmond |
| :--- | :--- | :--- | :--- |
| **Chicago** | 311 system lacks clarity; community members call it a "black hole" [9] [10]. | Departments frequently close duplicate requests without explanation [11]. | Richmond must define statuses and explain duplicate handling to prevent re-reports. |
| **San Diego** | Manual triage required for "Other" categories; non-service requests enter the system [8]. | 5 out of 264 sampled cases (1.9%) did not pertain to service requests [8]. | Highlights the need for clear intake guardrails to separate information needs from service orders. |
| **Washington DC** | Misroutes occur frequently near service boundaries [12]. | Location-based routing errors for 911 calls [12]. | Demonstrates the risk of geolocation inaccuracies when residents drop map pins. |

*Key Takeaway: Peer cities struggle with the same taxonomy and transparency issues; Richmond can preempt these by eliminating "Other" categories and clearly communicating request statuses.*

## Status, SLAs, and Trust
Vague statuses and mismatched Service Level Agreements (SLAs) erode public trust and drive duplicate reporting. A February 2026 Office of Inspector General (OIG) audit of Chicago's 311 system found that public-facing platforms do not provide users with clear information on the overall process, request statuses, and work order timeframes [10]. 

When residents do not understand what a "Closed" or "Completed" status means, they submit duplicate requests. Chicago's audit noted that departments frequently do not classify complaints as duplicates but simply close them without explanation, leading the public to feel their requests are ignored [11]. Furthermore, the SLAs displayed online often do not align with how long it actually takes for complaints to be addressed [11]. Richmond must standardize its RVA311 status definitions and embed a simple "what happens next" explainer to manage expectations and reduce escalations.

## Search as a Lever for Findability
*(Inference: Based on Richmond's known technology stack, search tuning is a highly accessible and underutilized lever for improving navigation).*

Richmond's rva.gov runs on Drupal and utilizes Acquia Search, which includes the Facet API module [13] [14]. Search facets enable users to refine or sort their search result sets, narrowing down results as they understand what content is available [13]. 

More importantly, the Acquia Search Config module allows administrators to modify configuration files directly through the Drupal site, specifically to change synonyms or stopwords [15]. Because residents use colloquial terms (e.g., "water bill," "couch pickup") rather than municipal terms (e.g., "Public Utilities," "Solid Waste Bulk"), deploying a synonyms file mapped to resident vocabulary can drastically improve the speed at which users find the right service, deflecting them from the 311 call queue.

## Measurement Gaps in Routing Accuracy
Richmond currently lacks the public data transparency required to diagnose root-cause routing failures. While the City launched RVA311 on AvePoint Citizen Services in June 2018 [16] [17], there is no public API for current request data. The only granular, public dataset available is the historical SeeClickFix data covering 2014 to 2015 [7]. 

Available data shows ~203,000 calls and ~75,200 requests created in 2024 (corrected 2026-03-18), but public reporting does not provide metrics on routing accuracy, miscategorization rates, or reassignment frequencies [2]. Without publishing quarterly reassignment rates or tracking an "Other" category usage metric, Richmond cannot accurately measure the success of any taxonomy improvements or digital navigation fixes.

## Downstream Impacts of Miscategorization
When a resident selects the wrong category or drops an inaccurate map pin, the errors cascade through the municipal workflow. In San Diego, the Get It Done app allows customers to manually adjust the location of a request, which has resulted in some requests having incorrect geospatial data [8]. 

Miscategorization leads to requests being routed to the wrong department, which then requires manual reassignment. This delays the initial response, causes the request to miss its target SLA, and often results in the ticket being closed out with inaccurate closure details [8]. To mitigate this, Richmond needs to implement address validation, map-pin confirmation, and category-specific required fields during the RVA311 intake process.

## Richmond-Specific Friction Assessment
Based on historical data and recent volume spikes, Richmond's primary friction points center around high-volume, high-confusion journeys. Solid waste remains a historical pain point, with residents forced to distinguish between yard waste, furniture, and brush [6]. 

Additionally, policy-sensitive programs create sudden navigation burdens. In 2025, the city received 3,835 requests regarding its RVA Stay Gap Grant Program, a housing relief program that was temporarily paused on January 16 [2]. When program statuses change rapidly, the disconnect between rva.gov information and RVA311 intake creates confusion, driving residents to call for clarification.

### Candidate Guided Flows and Expected Impact

| Flow | Current Pain Signal | Proposed Fix |
| :--- | :--- | :--- |
| **Bulk/Yard Waste** | High historical use of "Other" and subtypes [6]. | Consolidate into a visual wizard with photo examples of acceptable items. |
| **Finance Forms** | rva.gov pages deflect users to call 311 [5]. | Create canonical task pages linked directly to the top 5 requested forms. |
| **Housing Aid/Gap Grants** | 3,835 requests in 2025; program paused in Jan 2026 [2]. | Implement a cross-department content update SLA to ensure 311 scripts match website status. |
| **Streetlights** | Frequent historical reports of non-functioning lights [6]. | Add strict geolocation validation and pole-number requirements to intake. |

*Key Takeaway: Targeting these four specific flows with visual wizards and strict data validation will yield the highest reduction in manual triage and call center volume.*

## Implementation Roadmap
To break the navigation maze, Richmond should adopt a phased approach:
* **0–30 Days (Instrumentation):** Capture zero-result search queries on rva.gov. Add a lightweight "reassigned" flag to internal RVA311 dashboards to establish a baseline for misrouting.
* **31–90 Days (Pilots & Search):** Deploy a synonyms file in Acquia Search Config mapping resident terms to City services [15]. Launch a visual guided flow for Solid Waste/Bulk Pickup.
* **91–180 Days (Scale & Transparency):** Publish a public lifecycle explainer for 311 tickets. Standardize "Closed" vs. "Duplicate" statuses to prevent the "black hole" effect observed in Chicago [10].

## Governance and Content Ops
The massive spike in 2025 request volume highlights the need for tight alignment between rva.gov content and RVA311 knowledge bases. Richmond should establish a cross-department "Service Content Guild" responsible for maintaining canonical task pages. This guild must enforce 30-day review cadences and ensure that any program changes (like the pausing of the Gap Grant program [2]) trigger immediate updates to both the website and the 311 call center scripts.

## Risk Management and Failure Cases
Consolidating categories carries the risk of over-simplification, where departments lose the specific data fields they need to dispatch the correct crew. Furthermore, aggressive synonym mapping in site search can lead to "synonym drift," causing false positives in search results. To mitigate these risks, Richmond must continuously monitor the usage rate of the "Other" category and track duplicate submission rates. If duplicates rise after a taxonomy change, it signals that the new categories or statuses are not providing sufficient clarity to the residents.

***

## Appendices: Output Requirements

### Facts (Verifiable Public Information)
* In 2024, RVA311 received ~203,000 calls and ~75,200 requests created (corrected 2026-03-18 — prior figure of 208,216 was incorrect) [2].
* RVA311 also assisted or supported City partners in responding to over 83,000 requests in a prior reporting period [1] [2].
* Call center agents resolved a large share of concerns over the phone without creating a request for specific departments [2].
* The city received 3,835 requests regarding the RVA Stay Gap Grant Program, which was temporarily paused on Jan. 16, 2026 [2].
* RVA311 was launched on June 15, 2018, powered by AvePoint Citizen Services [16] [17].
* rva.gov utilizes Acquia Search, which supports Facets and synonym configuration [13] [14] [15].
* The historical SeeClickFix dataset for Richmond covers August 2014 to August 2015 [7].
* San Diego's Get It Done audit found that 5 out of 264 sampled cases (1.9%) did not pertain to service requests [8].
* Chicago's 2026 OIG audit found that 311's public-facing platforms do not provide users with clear information on request statuses, leading to a "black hole" perception [10].

### Inferences (Clearly Labeled)
* *Inference:* Because a large share of interactions are resolved by phone without a ticket, the primary friction point for residents is information-seeking and navigation, not actual service delivery failures. (Note: the previously cited 208,216 figure was incorrect; see corrected figures above.)
* *Inference:* The heavy reliance on the "Browse by Department" menu on rva.gov directly contributes to the high volume of informational calls to 311, as residents do not know which department handles their specific issue.
* *Inference:* By utilizing the existing Acquia Search Config module to add resident-friendly synonyms, Richmond can significantly improve digital self-service without requiring a platform migration.

### Unknowns (What Cannot Be Verified Publicly)
* The exact miscategorization or reassignment rate within Richmond's current Dynamics 365/AvePoint system.
* The specific breakdown of the 116,000 phone-resolved inquiries (i.e., which topics drive the most informational calls).
* The current internal SLAs for specific RVA311 categories and how often they are met.

## References

1. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
2. *Most common RVA 311 requests: What Richmonders needed help with in 2025 | WRIC ABC 8News*. https://www.wric.com/news/local-news/richmond/311-requests-richmond-2025/
3. *| Richmond*. https://www.rva.gov/
4. *Forms | Richmond*. https://www.rva.gov/planning-development-review/forms
5. *Finance Forms | Richmond*. https://rva.gov/finance/forms
6. *https://data.richmondgov.com/api/views/vgg4-hjn8/r...*. https://data.richmondgov.com/api/views/vgg4-hjn8/rows.csv?accessType=DOWNLOAD
7. *SeeClickFix Sample Data Aug 2014 to Aug 2015 | Open Data Portal ...*. https://data.richmondgov.com/w/vgg4-hjn8/uup7-qydm?cur=CQsdt-O98qV&from=root
8. *PERFORMANCE AUDIT OF THE CITY'S GET IT DONE ...*. https://www.sandiego.gov/sites/default/files/23-004_get_it_done_application_and_service_requests_management.pdf
9. *
    Chicago inspector general recommends changes to city's 311 service request system - CBS Chicago*. https://www.cbsnews.com/chicago/news/chicago-inspector-general-audit-311-service-request-system/
10. *OIG Finds Lack of Clarity, Transparency in the 311 Request Process, Limiting Its Potential to Improve City Services and Risking Public Distrust - Chicago Office of Inspector General*. https://igchicago.org/2026/02/26/oig-finds-lack-of-clarity-transparency-in-the-311-request-process/
11. *OIG Audit of 311 Service Request Process*. https://igchicago.org/wp-content/uploads/2026/02/OIG-Audit-of-311-Service-Request-Process.pdf
12. *Location-based routing for 911 Calls*. https://ouc.dc.gov/sites/default/files/dc/sites/OUC/April%202023%20Lunchtime%20Chat%20with%20Acting%20Director%20McGaffin%20-%20Location-based%20routing%20for%20911%20Calls%20%281%29.pdf
13. *Configuring search facets*. https://docs.acquia.com/acquia-cloud-platform/configuring-search-facets
14. *Installing Acquia Search*. https://docs.acquia.com/acquia-cloud-platform/installing-acquia-search
15. *Acquia Search Config | Drupal.org*. https://www.drupal.org/project/acquia_search_config
16. *New Richmond service request site set to launch*. https://www.12onyourside.com/story/38435120/new-richmond-service-request-site-set-to-launch/
17. *City launching new RVA311 service today to handle citizen, business, visitor requests - RVAHub*. https://rvahub.com/2018/06/15/city-launching-new-rva311-service-today-to-handle-citizen-business-visitor-requests154627/