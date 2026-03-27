
# RVA311 - From AvePoint/Dynamics Backbone to Actionable, Open-by-Default City Service Data

## Executive Summary

The City of Richmond's RVA311 system, powered by AvePoint Citizen Services on Microsoft Dynamics 365, serves as the central nervous system for non-emergency civic requests. While the platform successfully handles significant volume - with 2024 figures verified at ~203,000 calls and ~75,200 requests created (corrected 2026-03-18 - previously cited 208,216 was incorrect), and the city also noting over 83,000 requests assisted by partners in a prior period [1] - there are critical gaps in public data transparency, mobile user experience, and API accessibility. 

The system features a robust multi-channel intake process (phone, web, iOS, Android) and a sophisticated backend integration routing Public Works requests through Microsoft BizTalk into Trimble Cityworks [2] [3]. However, the lack of a documented public API and the obfuscation of the full 50+ request type taxonomy behind a JavaScript-rendered portal limit third-party innovation and civic transparency. To maximize the value of this infrastructure, Richmond must transition from a closed-loop operational tool to an open-by-default data platform.

## RVA311 at a Glance - 2018 AvePoint/Dynamics launch; 2024 volume ~203k calls

RVA311 operates on AvePoint Citizen Services, deploying Microsoft Dynamics 365, advanced machine learning, and IoT technologies to manage citizen requests [2]. The system replaced a fragmented legacy setup, centralizing requests that previously went to disparate call centers, council offices, or direct emails [2]. Verified 2024 figures: ~203,000 calls and ~75,200 requests created (corrected 2026-03-18 - previously cited 208,216 was incorrect). The City's official site also notes that RVA311 "provided assistance or supported our City partners in responding to over 83,000 requests" in a prior reporting period [1].

### Channel Footprint Confirmed - Phone, Web, iOS, Android, Internal Agent Portal

RVA311 supports a comprehensive omni-channel strategy. Citizens can submit requests via the 311 phone line (or 804-646-7000 for outside city limits), the RVA311.com web portal, and dedicated iOS and Android mobile applications [1]. Additionally, an internal portal is utilized by RVA311 Contact Center agents to process and route these requests [3].

## Channel Performance and Mix - Live channels; publish % split to drive investments

While the channels are well-established, the City does not publicly report the percentage breakdown of requests originating from each channel. Without this channel mix data, it is difficult to optimize call center staffing or prioritize digital user experience investments.

| Channel | Status | Evidence / Access Point | Known Issues | Data Gap |
| :--- | :--- | :--- | :--- | :--- |
| **Phone (311 / 804-646-7000)** | Live | Call center operates Mon-Sat [1] | Variable call volume [1] | No public % of total volume |
| **Web Portal (rva311.com)** | Live | Public portal with Insights page [4] [5] | JavaScript-heavy, hides taxonomy | No public % of total volume |
| **iOS App** | Live | App Store (3.5 stars, 13 ratings) [6] | Crashes, account creation bugs [6] | No public % of total volume |
| **Android App** | Live | Google Play (3.0 stars, 52 reviews) [7] | Search click-through failures [7] | No public % of total volume |
| **Internal Agent Portal** | Live | Used by Contact Center agents [3] | N/A | Not publicly quantified |

**Key Takeaway:** The City has successfully deployed a multi-channel intake system, but the lack of public channel-share metrics obscures user behavior trends. Instrumenting and publishing these metrics is a critical next step.

## Request Taxonomy and Department Groups - Seven groups public; extract 50+ request types

The RVA311 system partners with over 30 different departments, agencies, and teams, organized publicly into distinct department groups [1]. However, the granular list of ~50+ specific request types is not published as a static directory; users must navigate the JavaScript-based portal to view them [4].

| Department Group | Publicly Listed Subdomains / Request Categories | Evidence |
| :--- | :--- | :--- |
| **Public Works** | Solid Waste, Bulk and Brush, Grounds Maintenance, Right of Way Management, Transportation and Safety, Parking Enforcement, Urban Forestry, Streetlight Engineering, Streetlight Maintenance | [1] |
| **Public Utilities** | Storm Water, Waste Water | [1] |
| **Social Services** | Benefit Application and Eligibility, Adult Services, Child Protective Services, Homeless Services | [1] |
| **Finance and Revenue** | Personal Property Taxes, Business Property Taxes, Real Estate Taxes, Business Licensing, Collections | [1] |
| **Planning and Development** | Zoning and Permitting, Code Enforcement | [1] |
| **Other Partners** | Non-emergency Police, Animal Care and Control, Office of Elections | [1] |

**Key Takeaway:** While the high-level taxonomy is transparent, the lack of a canonical, easily scrapeable list of all request types creates friction for residents and civic developers. The City should publish a static "RVA311 Request Catalog."

## Integration Architecture - BizTalk to Cityworks (DPW) confirmed; non-DPW flows need clarity

The backend architecture of RVA311 relies heavily on Microsoft ecosystem integrations to route requests without human intervention where possible [2]. 

| System | Role in RVA311 Ecosystem | Notes / Evidence |
| :--- | :--- | :--- |
| **AvePoint Citizen Services (Dynamics 365)** | Core CRM, intake, case management, and public portal backend | Routes requests to appropriate departments; provides public tracking [2] [3]. |
| **Microsoft BizTalk** | Enterprise integration bus | Sends inbound requests from Dynamics to downstream systems [2] [3]. |
| **Trimble Cityworks** | Work order management (primarily DPW) | Integrates easily through BizTalk without complicating the citizen interface [2] [3]. |
| **ESRI GIS** | Mapping and location services | Used for address validation and mapping requests [3]. |
| **Azure Entra ID / Active Directory** | Identity and access management | Manages internal authentication [3]. |

**Key Takeaway:** The automated flow from Dynamics 365 through BizTalk to Cityworks is well-documented for Public Works [2]. However, workflows for non-DPW departments (like Social Services or Finance) likely rely on native Dynamics routing or manual agent handoffs, representing potential SLA bottlenecks.

## Mobile Experience - 3.0 stars Android (52), 3.5 stars iOS (13); fix sign-in, search, crashes

While the mobile apps provide 24/7 access, user reviews highlight significant reliability issues that threaten self-service adoption.

| Platform | Rating / Volume | Notable User-Reported Issues | Evidence |
| :--- | :--- | :--- | :--- |
| **Android** | 3.0 stars (52 reviews) | Search feature results fail to click through to the required page (Dec 2025). | [7] |
| **iOS** | 3.5 stars (13 ratings) | App crashes before loading; account creation confirmation links fail to work. | [6] |

**Key Takeaway:** Mobile friction directly increases expensive call center volume. A dedicated 60-day reliability sprint focusing on core navigation, search, and authentication is required to stabilize these channels.

## Data Access and API Posture - No public API docs found; enable nightly open data

A major constraint of the current RVA311 deployment is the apparent lack of a public-facing API. 

| Data Source | Accessibility | API / Open Data Status |
| :--- | :--- | :--- |
| **RVA311 Web Portal** | Publicly accessible via browser | No public API documentation found; relies on internal endpoints [4]. |
| **AvePoint Documentation** | Vendor case studies available | Highlights internal integrations (BizTalk) but mentions no public API [2]. |
| **Socrata (Legacy Data)** | Open dataset (vgg4-hjn8) | Contains historical SeeClickFix data (2014-2015), but not live Dynamics data. |

**Key Takeaway:** Without a live API, civic tech developers cannot build custom dashboards or integrations. If AvePoint/Dynamics cannot expose a secure read-only API, the City must implement nightly CSV/JSON exports of anonymized request data to a public repository like Socrata.

## Historical Continuity - Map SeeClickFix (2014-2018) to current categories

The transition from SeeClickFix to AvePoint in 2018 fundamentally changed the system's scope. 

| Legacy Domain (SeeClickFix) | Current RVA311 Group | Continuity Notes |
| :--- | :--- | :--- |
| **Potholes / Street Maintenance** | Public Works | Direct mapping; core DPW function [1] [8]. |
| **Trash / Bulk Pickup** | Public Works (Solid Waste) | Direct mapping [1]. |
| **Tax / Finance Inquiries** | Finance and Revenue | Net-new capability introduced with Dynamics 365 [1]. |
| **Social Services** | Social Services | Net-new capability introduced with Dynamics 365 [1]. |

**Key Takeaway:** While infrastructure requests map cleanly across the 2018 platform shift, the addition of Finance and Social Services represents a massive expansion of the 311 mandate. Analysts must account for this when comparing historical volume trends.

## Metrics and Governance - Publish SLAs, owners, channel mix, taxonomy

To mature the RVA311 platform, Richmond must implement stricter public governance. Currently, the portal allows users to track statuses (Unprocessed, Assigned, In Progress, On Hold, Completed) [4], but lacks public SLA targets. The City should publish a governance charter that names service owners per request type, establishes baseline SLAs, and reports monthly on channel mix and average days-to-close.

## Implementation Roadmap - Quick wins to modernization

1. **0-90 Days:** Extract and publish a static Request Catalog on rva.gov. Execute a mobile app reliability sprint to fix iOS crashes and Android search bugs [7] [6].
2. **3-6 Months:** Establish nightly open data exports of anonymized RVA311 tickets to bridge the API gap. Publish per-department workflow diagrams.
3. **6-12 Months:** Evaluate the aging Microsoft BizTalk integration layer [3] for potential modernization to Azure Logic Apps or Service Bus to ensure long-term stability with Cityworks.

## Risks and Mitigations - Integration fragility, UX debt, data privacy

* **Integration Risk:** Relying on BizTalk for critical Cityworks routing introduces legacy maintenance risks. Mitigation: Implement proactive health monitoring and failover designs.
* **UX Debt:** Poor mobile app ratings [7] [6] depress digital adoption. Mitigation: Continuous UX testing and transparent release notes.
* **Data Privacy:** Expanding 311 to include Social Services and Finance increases PII risks. Mitigation: The City currently allows anonymous submissions and hides PII from the public portal [1]; these strict redaction policies must be maintained in any future open data exports.

## References

1. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
2. *RVA 311 | AvePoint*. https://www.avepoint.com/case-studies/rva311
3. *Business Systems Analyst - Richmond*. https://www.governmentjobs.com/careers/richmond/jobs/newprint/4858339
4. *Fetched web page*. https://www.rva311.com/rvaone#/faq
5. *Home | RVA311.COM*. https://www.rva311.com/rvaone
6. *RVA311 - App Store - Apple*. https://apps.apple.com/us/app/rva311/id1408330609
7. *RVA311 - Apps on Google Play*. https://play.google.com/store/apps/details?id=com.richmondgov.com.rva311&hl=en_US
8. *Potholes and Street Maintenance | Richmond*. https://www.rva.gov/public-works/potholes-and-street-maintenance