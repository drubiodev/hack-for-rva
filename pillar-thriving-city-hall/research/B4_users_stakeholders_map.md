# Thriving City Hall: Who Matters, What They Need, and How to Win Support

## Executive Summary
Success for the "Thriving City Hall" prototypes hinges on navigating a complex web of operational gatekeepers, compliance mandates, and political priorities. For the resident service navigation problem, historical data from the City Auditor reveals a significant trust gap: in a past survey, only 42% of residents felt city staff resolved their issues, and just 39% said staff did what they promised [1]. Overcoming this requires securing the sponsorship of Peter D. Breil, Director of Citizen Service and Response [2], and aligning with City Council's recent "Digital Equity Implementation Plan" (RES. 2024-R026) [3]. For the procurement modernization problem, solutions must demonstrate strict adherence to the Virginia Public Procurement Act (VPPA) [4] to satisfy the City Auditor and Finance departments. 

## Purpose and Scope
This report maps the critical stakeholders for two targeted City Hall problems: Resident Service Navigation and Procurement Modernization. Success hinges on aligning with high-power sponsors (such as 311 leadership, IT, and Procurement), proving equity-aligned outcomes, and embedding compliance-by-design. By understanding who matters and what moves them, hackathon teams can design prototypes that survive post-event scrutiny and achieve enterprise adoption.

## Problem Context and Objectives
Both targeted problems sit under strong governance structures and intense public scrutiny. The resident navigation (311) problem is governed by the Department of Citizen Service and Response and must operate within the political reality of City Council's equity lens. The 2024 Digital Equity Implementation Plan explicitly calls out market failures that have excluded lower-income communities from digital access, making inclusive design a mandate, not an option [3] [5]. Meanwhile, procurement modernization is strictly bound by the Virginia Public Procurement Act (VPPA) [4] and subject to rigorous oversight by the Office of the City Auditor, which plans and conducts audits to ensure effective coverage of the City of Richmond [6].

## Stakeholder Landscape: Resident Service Navigation
The 311 ecosystem involves a delicate balance between residents seeking help, agents routing requests, and departments executing the work. 

| Stakeholder Group | Interests / Pain Points | Power / Influence | What They Need to See for Support | Documented Positions |
| :--- | :--- | :--- | :--- | :--- |
| **Residents** (First-time, repeat, non-English, seniors, mobile-only) | Need easy access to services; pain from unresolved issues or complex navigation. | High (Collective political influence) | Multilingual, low-bandwidth mobile UX; proof of first-contact resolution. | 2016 Auditor report: Only 42% felt issues were resolved [1]. |
| **311 Staff** (Director Peter D. Breil, supervisors, agents) | Need efficient routing; pain from high call volumes and angry callers. | High (Operational gatekeepers) | Seamless integration with existing workflows; reduction in call handle times. | RVA311 operates Mon-Sat to deflect non-emergency calls from 911 [7]. |
| **rva.gov Website Team** (City IT, Tech Dynamism) | Need system stability and security; pain from unvetted integrations. | High (Technical gatekeepers) | Lightweight integration (API proxy/embed) avoiding core CMS disruption. | N/A |
| **Department Staff** (Public Works, Utilities, etc.) | Need accurate tickets; pain from misrouted requests and SLA hits. | Medium (Service owners) | Dynamic routing rules that demonstrably reduce misrouted tickets. | N/A |
| **City Council Members** | Need constituent satisfaction; pain from complaints. | High (Funding/Policy) | Budget-neutral pilot metrics; alignment with digital equity goals. | Passed Digital Equity Implementation Plan (RES. 2024-R026) [3] [8]. |
| **Community Organizations & Libraries** | Need resources to help residents; pain from digital divide. | Medium (Distribution partners) | Printable guides; assisted-service pilot support. | Libraries undergoing retrofits for digital collaboration [9]. |

### 311 Leadership and Agents
Securing executive sponsorship is critical. Peter D. Breil, Director of Citizen Service and Response, is the visible owner of RVA 311 [2]. Hackathon teams must secure his sponsorship and co-design agent scripts with frontline staff to de-risk change resistance. High-influence gatekeepers can fast-track access to data and change approvals.

### Departments Receiving Tickets
Departments receiving misrouted 311 tickets bear workload and SLA risk. The 2016 audit flagged incomplete answers and poor follow-through as systemic issues [1]. Prototyping dynamic routing and "return-to-sender" prevention rules for top misrouted categories will be essential to win departmental buy-in.

### Residents With Access Barriers
Solutions that overlook non-English speakers, seniors, and mobile-only users will face Council scrutiny. Council unanimously advanced a "Digital Equity Implementation Plan" declaring high-speed internet a public necessity [3] [5]. Prototypes must feature multilingual, low-bandwidth mobile UX with SMS/voice alternatives aligned to 311's Monday-Saturday operating hours [7].

## Stakeholder Landscape: Procurement Modernization
Procurement in Richmond is a high-stakes compliance environment where speed must be balanced against strict legal and fiscal controls.

| Stakeholder Group | Interests / Pain Points | Power / Influence | What They Need to See for Support | Documented Standards |
| :--- | :--- | :--- | :--- | :--- |
| **Procurement Officers** | Need compliance and efficiency; pain from manual tracking. | High (Process owners) | Audit trails, Segregation of Duties (SoD), competitive thresholds. | Must comply with Virginia Public Procurement Act (VPPA) [4]. |
| **Finance/Budget Staff** | Need fiscal compliance; pain from budget overruns. | High (Fiscal gatekeepers) | Real-time budget validation and transparent reporting. | N/A |
| **City Auditor** | Need accountability and transparency; pain from opaque processes. | High (Oversight) | Immutable logs, FOIA-ready data exports, clear control design. | Conducts audits for effective coverage of the City [6]. |
| **Department Directors** | Need fast contract execution; pain from cycle-time delays. | Medium (Internal customers) | Speed, predictability, and reduced friction in requests. | N/A |
| **City Council Members** | Need fiscal oversight; pain from procurement scandals/delays. | High (Legislative oversight) | Clear value-for-money narratives and compliance dashboards. | Governmental Operations Standing Committee oversees related ordinances [10]. |
| **Vendors and Contractors** | Need fair access and timely payment; pain from complex bidding. | Low (External users) | Simplified vendor portals and clear status tracking. | N/A |

### Procurement Officers
Procurement officers require audit trails, segregation of duties, and competitive thresholds. Any prototype must prove auditability and align artifact fields to the VPPA and City policy [4].

### Finance/Budget and City Auditor
The City Auditor is a credibility multiplier and a heat check. The Auditor's office selects and reports audits [11]. Early alignment with the Auditor on pilot measurement methods and control design reduces post-pilot surprises.

### Department Directors and Vendors
Department directors and vendors need cycle-time reduction and predictability. While they have less formal power over the system's adoption than compliance officers, their user experience dictates the system's practical success.

## Cross-Cutting External Influencers
External influencers shape the environment in which these solutions will be deployed.

| Influencer | Lever | Risk / Opportunity | Required Engagement Step |
| :--- | :--- | :--- | :--- |
| **City Council** | Policy & Funding | Risk: Rejection if equity is ignored. Opportunity: Championing via Digital Equity Plan [3]. | Present budget-neutral dashboards tied to equity metrics. |
| **Libraries & CBOs** | Infrastructure | Opportunity: Assisted onboarding for marginalized groups [9]. | Run assisted-service pilots at branch locations. |
| **City IT / Vendors** | Technical Infrastructure | Risk: CMS bottlenecks and security blocks. | Validate change-control lead times early. |

## Power-Interest Matrix
To effectively manage post-hackathon adoption, stakeholders must be engaged according to their power and interest levels.

| Quadrant | Strategy | Resident Navigation Stakeholders | Procurement Stakeholders |
| :--- | :--- | :--- | :--- |
| **High Power / High Interest** | **Manage Closely** | 311 Director (Breil) [2], City IT, Council Leadership | Procurement Officers, Finance, City Auditor [6] |
| **High Power / Low Interest** | **Keep Satisfied** | Department Directors (receiving tickets) | Department Directors (requesting contracts) |
| **Low Power / High Interest** | **Keep Informed** | Community Orgs, Libraries [9] | Vendors and Contractors |
| **Low Power / Low Interest** | **Monitor** | General Public (until pilot results) | General Public |

## Evidence-Backed Adoption Requirements
To move from prototype to pilot, specific proofs must be delivered to high-power stakeholders.

### Resident Navigation Prototype: 90-Day Proof Pack
The prototype must anchor its success criteria in first-contact resolution and accurate routing. The team must commit to publishing a 90-day pilot scorecard showing baseline versus improvement on misroutes, resolution time, and "kept promise" follow-through, directly addressing the historical 39% satisfaction rate on kept promises [1].

### Procurement Prototype: Compliance-by-Design
For the procurement prototype, teams must prove auditability through immutable logs, segregation of duties, and conflict disclosures. Artifact fields must map directly to the Virginia Public Procurement Act (VPPA) [4], and the system must generate FOIA-ready exports to satisfy the City Auditor.

## Engagement Plan and Sequencing
A phased approach ensures technical viability before political exposure.

### Pre-Pilot (Weeks 0-2)
Focus on sponsorships, access, and risk checks. Secure written sponsorship from Director Breil [2] and confirm vendor-of-record constraints with City IT.

### Pilot (Weeks 3-12)
Co-design agent scripts and routing rules with frontline staff. Run assisted-service pilots at two library branches (leveraging recent retrofits [9]) and two CBO partners to measure completion rates for seniors and non-English speakers.

### Post-Pilot (Weeks 13-16)
Invite the Auditor's team to review pilot measurement methods. Equip City Council with a one-page dashboard showing request volumes shifted from 911 to 311 [7] and budget-neutral outcomes.

## Metrics That Matter
Tracking the right metrics is essential for proving value and securing scale.

| Problem Area | Metric | Definition | Target Threshold | Cadence |
| :--- | :--- | :--- | :--- | :--- |
| **Resident Nav (311)** | First-Contact Resolution | % of issues resolved without transfer/callback | > 60% (up from 42% [1]) | Weekly |
| **Resident Nav (311)** | Misroute Rate | % of tickets sent to wrong department | < 10% | Weekly |
| **Resident Nav (311)** | Digital Equity Reach | Usage by non-English/mobile-only users | Baseline + 20% | Monthly |
| **Procurement** | Cycle Time | Days from request to contract execution | 20% reduction | Monthly |
| **Procurement** | VPPA Compliance | % of transactions passing automated SoD checks | 100% [4] | Weekly |

## Risks, Failure Cases, and Guardrails
Anticipating failure modes prevents the erosion of trust.

| Risk | Early Warning Signal | Mitigation | Owner |
| :--- | :--- | :--- | :--- |
| **Trust Erosion** | High rate of incomplete answers/broken promises [1]. | Implement closed-loop SMS confirmations and SLA tracking. | 311 Supervisors |
| **Accessibility Misses** | Low adoption in target neighborhoods. | Deploy multilingual UX and partner with libraries for assisted use [9]. | Product Team |
| **Compliance Shortfalls** | Auditor flags missing logs. | Embed VPPA controls [4] and immutable logging by design. | IT / Procurement |
| **Off-Hours Dead Ends** | High abandonment outside Mon-Sat hours [7]. | Graceful deferral scripts with emergency 911 guidance. | 311 Agents |

## Implementation Partners and Resources
Leveraging existing city infrastructure accelerates deployment.

| Partner | Role | Resource Ask | Success Measure |
| :--- | :--- | :--- | :--- |
| **Richmond Public Libraries** | Assisted-service hubs | Use of retrofitted digital spaces [9] | Number of assisted sessions completed |
| **City IT / Tech Dynamism** | Web integration | API access / Change control approval | Zero downtime during deployment |
| **Office of the City Auditor** | Compliance validation | Review of control design [11] | Zero critical audit findings |

## Appendices
* **Links & References:**
 * Citizen Service and Response / Peter D. Breil [2]
 * About RVA 311 (Hours and Mission) [7]
 * Office of City Auditor 2016-04 Report (Satisfaction Data) [1]
 * Digital Equity Implementation Plan (RES. 2024-R026) [3] [5] [8]
 * VPPA Compliance Ordinance [4]
 * FY2022-FY2026 CIP (Library Retrofits) [9]
* **Glossary:**
 * **VPPA:** Virginia Public Procurement Act.
 * **SoD:** Segregation of Duties.
 * **FOIA:** Freedom of Information Act.
 * **SLA:** Service Level Agreement.

## References

1. *Office of the City Auditor*. https://www.rva.gov/sites/default/files/Auditor/documents/2016/2016-04_ServiceEffortsAndAccomplishments.pdf
2. *Citizen Service and Response | Richmond*. https://rva.gov/citizen-service-and-response
3. *
	City of Richmond - File #: RES. 2024-R026
*. https://richmondva.legistar.com/LegislationDetail.aspx?ID=6791846&GUID=7A3D4E77-4A39-4BAE-AB85-985C3B881BA5
4. *INTRODUCED: January 12, 2026 AN ORDINANCE No. ...*. https://richmondva.legistar.com/View.ashx?M=F&ID=15182433&GUID=B68DBC6E-37E3-46DF-AF06-AC9DF2F91584
5. *
			
				Richmond City Council approves resolution to improve internet access |  Richmond Free Press | Serving the African American Community in Richmond, VA
			
		*. https://m.richmondfreepress.com/news/2024/sep/12/richmond-city-council-approves-resolution-to-improve-internet-access/
6. *Office of the City Auditor*. https://www.rva.gov/office-city-auditor/home
7. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
8. *Richmond City Council passes resolution to improve internet speed throughout the city | WRIC ABC 8News*. https://www.wric.com/news/local-news/richmond/richmond-city-council-passes-resolution-to-improve-internet-speed-throughout-the-city/
9. *FY2022 - FY2026 Proposed Capital Improvement Plan*. https://www.rva.gov/sites/default/files/2021-03/FY2022%20-%20FY2026%20Proposed%20Capital%20Improvement%20Plan%20-%20Online%20Version.pdf
10. *
	City of Richmond - Meeting of Governmental Operations Standing Committee on 10/22/2025 at 1:00 PM
*. https://richmondva.legistar.com/MeetingDetail.aspx?ID=1288549&GUID=716DA95B-CE73-4CD9-BA93-9D16A8D3B553&Options=&Search=
11. *Audit Guide | Richmond*. https://www.rva.gov/office-city-auditor/audit-guide