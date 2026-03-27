# Benchmark Scan — National Comparables

A Thriving City Hall — prior art in resident service navigation and government procurement tools.

Note: All entries are based on publicly known information. Teams should verify current status before citing in demos.

---

## Resident Service Navigation & 311

### Boston 311 (SeeClickFix)
- **What it is:** Boston uses SeeClickFix for resident service requests with a mobile app and web interface; residents describe issues in plain language and the system suggests categories.
- **Relevance:** Richmond used SeeClickFix from 2014–2018 before switching to AvePoint. The historical Socrata dataset (vgg4-hjn8) contains this era of data.
- **Notable:** Boston Open311 API provides programmatic access to request types and statuses — a capability Richmond's current platform lacks.
- **URL:** https://www.boston.gov/departments/311

### NYC 311 (Open API + Open Data)
- **What it is:** NYC 311 is one of the most mature 311 systems in the US with a full open API, public dataset (311 Service Requests going back to 2010), and mobile app.
- **Relevance:** NYC's open data approach is the model that Richmond's current system does not support. NYC's dataset demonstrates what's possible when 311 data is made public — Richmond's post-2018 gap is notable by comparison.
- **Data:** NYC Open Data: `data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9`
- **Notable:** NYC has explored AI-assisted routing and smart search over 311 categories.

### San Francisco 311 (SF311)
- **What it is:** SF311 offers an Open311 API and public dataset via DataSF, with service type taxonomies and routing logic documented.
- **Relevance:** SF's service type taxonomy and plain-language category descriptions are a useful reference model for building a 311 helper without requiring API access.
- **URL:** https://data.sfgov.org/

### Chicago Open311
- **What it is:** Chicago's 311 system uses Open311 (a national standard), providing documented APIs for service types, request submission, and status lookup.
- **Relevance:** Open311 standard defines the vocabulary and schema that Richmond could theoretically adopt; useful reference for understanding what a well-structured 311 API looks like.
- **URL:** https://www.chicago.gov/city/en/depts/311.html

### Code for America — Honolulu (Ohana)
- **What it is:** Ohana is an open-source resource directory tool initially built by Code for America for Honolulu. The pattern — plain-language search over government services — is directly relevant to the rva.gov Smart Search concept.
- **Relevance:** Demonstrates feasibility of building a plain-language service navigator over public government content.

---

## Government Procurement Tools

### USASpending.gov
- **What it is:** The federal government's official spending transparency site, showing contract awards, grants, and spending by agency, vendor, and geography.
- **Relevance:** Free API with no key required for basic queries; useful for the Cross-Source Contract Finder concept. Also demonstrates what transparency looks like when spending data is well-structured.
- **URL:** https://www.usaspending.gov/

### FPDS (Federal Procurement Data System)
- **What it is:** The authoritative source for federal contract award data, accessible through usaspending.gov.
- **Relevance:** Understanding FPDS schema is useful for teams building procurement tools that need to cross-reference Richmond vendor activity against federal contracts.

### OpenGov (various cities)
- **What it is:** OpenGov is a SaaS platform used by many municipalities for procurement and budgeting transparency. Some cities use it for public-facing contract portals.
- **Relevance:** Some Virginia localities use OpenGov for procurement. Richmond's prior procurement portal used a related tool. Knowing OpenGov's data export formats can help teams build compatible tools.

### Iowa State Procurement Portal
- **What it is:** Iowa's statewide procurement portal with searchable contracts and expiry tracking — a model for what a contract dashboard could look like.
- **Relevance:** Demonstrates feasibility of a contract expiry dashboard built on structured public data.

### Virginia eVA
- **What it is:** Virginia's statewide electronic procurement system. Data available on data.virginia.gov as CSV export.
- **Relevance:** Direct data source for the Cross-Source Contract Finder concept. Virginia agencies (including Richmond) use eVA for many purchases.
- **URL:** https://eva.virginia.gov/

---

## Government Chatbot & AI Navigation Tools

### USA.gov (BETA)
- **What it is:** The federal government's plain-language service finder; AI-assisted search over federal services.
- **Relevance:** Demonstrates the pattern of plain-language query → service match → official link. Relevant model for the Plain-Language 311 Helper and RVA.gov Smart Search.

### Bloomington, IN — "Ask Bloomington"
- **What it is:** A conversational AI assistant built to help residents find city services and FAQs.
- **Relevance:** An example of a city deploying a service navigation chatbot — and the risks that come with it (wrong answers, outdated info, confidence calibration).

### Failed government chatbots (cautionary reference)
- Several city and federal chatbots have failed due to: confidently wrong answers, inability to handle edge cases, and lack of human fallback. Lessons: always show source, always provide a "talk to staff" escape hatch, and never claim the tool is authoritative.
