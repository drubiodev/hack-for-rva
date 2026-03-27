# Buildable-by-Weekend Boundaries for Thriving City Hall MVPs

## Executive Summary

To ensure hackathon teams build safe, feasible, and judge-ready prototypes for the "A Thriving City Hall" track, strict scope boundaries must be enforced. The City of Richmond's data landscape presents specific constraints: RVA311 handles massive volumes (over 163,000 calls in 2024) without a public API [1], and procurement data is updated monthly rather than in real-time [2]. 

The most critical insights for teams are:
* **No live integrations:** RVA311 and internal financial systems (Oracle RAPIDS) are strictly off-limits. All prototypes must be informational and advisory.
* **Emergency triage is mandatory:** Any hint of an urgent health or safety issue must immediately halt the flow and prompt the user to call 911 [3].
* **Compliance is human-driven:** Legal determinations, contract award recommendations, and SAM.gov debarment conclusions cannot be automated. Prototypes must only surface data flags.
* **Transparency is a feature:** Every piece of data must include a source link, a freshness timestamp, and a clear disclaimer that the tool is not an official City application.

## Objective and Decision Frame

The goal of this framework is to define the hard lines that hackathon teams must not cross. These boundaries exist because the underlying data does not support real-time integration, because crossing them could cause severe civic harm (e.g., misrouting an emergency), or because the scope is simply not buildable within a 48-hour window. By adhering to these "must not cross" and "must include" boundaries, teams will deliver advisory, link-out prototypes that the City could realistically pilot.

## Data Landscape and Constraints

Understanding what is public, what is private, and how fresh the data is will dictate the architecture of every MVP.

### RVA311 Platform Realities
RVA311 operates on an AvePoint/Dynamics 365 platform integrated with Cityworks [4]. In 2024, the call center handled over 163,000 calls, averaging 13,500 per month [1]. There is no documented public API for live ticket submission. Attempting to reverse-engineer submissions risks polluting the City's live queue and delaying actual resident services.

### Procurement Data Scope
The City Contracts dataset on the Open Data Portal (Socrata xqn7-jvv2) provides a 5-year window of open and closed contracts across 9 fields [2]. Crucially, this data is updated monthly—with the last update noted as March 16, 2026 [2]. It may not reflect recent amendments, making real-time accuracy claims impossible.

### OpenGov Bids/RFPs
The City manages formal invitations for bids through OpenGov, which provides transparency into successful and unsuccessful bidders and bid amounts [5]. Teams should use OpenGov links for award information rather than replicating the data as authoritative.

### SAM.gov Exclusions
Federal Acquisition Regulation (FAR) 9.404 requires agencies to check the System for Award Management (SAM) for excluded parties [6]. However, determining actual eligibility requires reading the specific "cause and effect" language of an exclusion [7]. Prototypes can only flag potential matches, not make definitive debarment determinations.

## Hard Scope Boundary Tables

The following tables define the non-negotiable boundaries for both problem tracks.

### Resident Service Navigation Boundaries

| Item | In/Out | Rationale & Evidence | Risk if Violated |
| :--- | :--- | :--- | :--- |
| **Live RVA311 data integration** | OUT | No public API exists; system handles 163k+ calls/year [1]. | Broken prototype; polluting live City systems. |
| **Submission of actual service requests** | OUT | Requires authenticated integration with Dynamics 365 [4]. | False promises to residents; lost service requests. |
| **Official City position claims** | OUT | Hackathon projects are unvetted third-party tools. | Legal liability; public misinformation. |
| **Routing urgent health/safety queries** | OUT | 911 is strictly for emergencies; 804-646-5100 for non-emergencies [3]. | Severe civic harm; delayed emergency response. |
| **Eligibility determinations** | OUT | Complex rules require human caseworkers. | Denying eligible residents or promising false benefits. |
| **Full conversational chatbot** | OUT | Too broad to build safely in 48 hours. | Hallucinations; scope creep; failed demo. |
| **Human fallback (Call 311 link)** | IN | 311 is the official fallback for all non-emergencies [1]. | Dead-end user experiences. |
| **Source attribution for all info** | IN | Builds trust and allows verification. | Lack of credibility. |
| **"Not an official tool" disclosure** | IN | Manages user expectations. | Brand confusion for the City. |
| **"I don't know / call 311" handling** | IN | Safe failure mode for edge cases. | Providing incorrect or hallucinated answers. |

### Procurement Review Boundaries

| Item | In/Out | Rationale & Evidence | Risk if Violated |
| :--- | :--- | :--- | :--- |
| **Legal compliance determinations** | OUT | Requires certified contracting officers. | Legal exposure; flawed procurement processes. |
| **Recommending contract awards** | OUT | Violates competitive bidding integrity. | Procurement protests; ethical violations. |
| **Accessing internal financial systems** | OUT | Oracle RAPIDS is strictly internal for employees [8]. | Security breach; immediate disqualification. |
| **Claiming real-time accuracy** | OUT | Socrata dataset is only updated monthly [2]. | Misrepresenting contract status or values. |
| **Debarment determinations** | OUT | SAM.gov requires human review of exclusion types [7]. | Falsely labeling a vendor as ineligible. |
| **"Advisory only" disclaimer** | IN | Protects the City and the user. | Users treating prototype output as legally binding. |
| **Data source and date attribution** | IN | Socrata data was last updated March 16, 2026 [2]. | Hidden data staleness. |
| **Amendments caveat** | IN | Datasets may not reflect mid-month contract changes. | Financial inaccuracies. |

## Risk and Harm Guardrails

To ensure prototypes do not cause real-world harm, teams must implement specific UI and logic guardrails.

### Emergency and Safety Triage
Any user input containing keywords related to health, safety, violence, or immediate danger must trigger a blocking modal. This modal must instruct the user to call 911 for emergencies or 804-646-5100 for non-emergency public safety [3]. The application must not attempt to answer the query.

### Legal/Compliance Non-Determination
For procurement tools, SAM.gov data must be presented strictly as a "Flag." The UI must never use words like "Eligible," "Ineligible," "Pass," or "Fail." A mandatory global banner must state: "Advisory only — verify in official systems."

### Data Freshness and Amendments
Because the City Contracts dataset is updated monthly [2], every data card or table row must display a prominent timestamp (e.g., "Data as of March 16, 2026"). A persistent note must acknowledge that the data may not reflect recent contract amendments.

## MVP Design Patterns That Fit 48 Hours

Teams should utilize these safe, feasible design patterns to ensure they have a working demo by Sunday.

### Resident Navigator MVP
Focus on 8–10 high-frequency intents (e.g., bulk trash, potholes, tax deadlines). Build source-backed content cards that explain what the service is, who qualifies, and how to apply. Every card must end with a deep link to the official RVA.gov page and a "Call 311" fallback button.

### Procurement Reviewer MVP
Build a "Contract/Vendor Fact Sheet" generator. Pull data from the Socrata CSV/OData endpoint [2], append links to the OpenGov portal for award details [5], and display a simple "SAM.gov Flag Present? (Yes/No)" indicator with a timestamp. 

### Shared Components
Both tracks should utilize a standard "Source Badge" (linking to the origin data), a "Freshness Banner" (showing the last update time), and the "Emergency Modal" (for the resident track).

## Language for Explaining Scope to Judges

Teams should use the following pre-approved framing during their pitches to demonstrate they understand civic tech constraints:

**For Resident Service Navigation:**
> "To ensure resident safety and prevent misinformation, our prototype is strictly advisory. We do not integrate with the live RVA311 system to avoid polluting actual service queues. Instead, we route users to official City channels and include hard fallbacks to 911 for emergencies and 311 for complex edge cases."

**For Procurement Review:**
> "Our tool acts as a data aggregator, not a compliance officer. Because City contract data is updated monthly, every record is time-stamped and includes a disclaimer that it may not reflect recent amendments. We surface SAM.gov records as advisory flags for human review, ensuring we never make automated legal determinations."

## Pre-Demo Scope Validation Checklist

Teams must pass this binary checklist before presenting:

* [ ] **Disclaimers:** Is the "Not an official City tool / Advisory only" banner visible on all screens?
* [ ] **Attribution:** Does every piece of data show its source link and a freshness timestamp?
* [ ] **Emergency Handling (Resident):** Do urgent keywords trigger a hard stop and a 911 prompt?
* [ ] **No Submissions:** Are all forms strictly informational (no backend POST requests to City systems)?
* [ ] **Compliance (Procurement):** Are SAM.gov results labeled as "Flags" rather than "Determinations"?
* [ ] **Fallbacks:** Is the "Call 311" option easily accessible from every state?

## Failure Cases and Cautionary Examples

Understanding what *not* to build is as important as knowing what to build.

* **The Auto-Submitter:** A team builds a script that automatically emails 311 or tries to POST to the Cityworks backend. *Result:* Disqualification for risking denial-of-service to critical city infrastructure.
* **The "Know-It-All" Bot:** A team uses an unconstrained LLM to answer any resident question. *Result:* The bot hallucinates tax deadlines or eligibility requirements, creating severe civic harm.
* **The Automated Judge:** A procurement tool that outputs "DO NOT AWARD" next to a vendor name based on a fuzzy SAM.gov match. *Result:* Fails judging for violating FAR guidelines that require human review of exclusion causes [7].

## Testing and Validation Plan

To prove safety in 48 hours, teams should conduct dry-runs using seeded scenarios. Red-team the resident app by typing emergency keywords (e.g., "fire," "hurt," "gun") to ensure the 911 modal triggers instantly. For procurement, verify that the timestamps match the Socrata metadata (March 16, 2026) [2] and that all external links resolve correctly to OpenGov or RVA.gov.

## Implementation Timeline

* **Day 1 (Friday):** Establish data wiring (Socrata CSVs, static RVA.gov content) and build the UI skeleton. Implement the global disclaimers.
* **Day 2 (Saturday):** Build the content cards and implement the hard guardrails (Emergency modal, SAM.gov flag logic). 
* **Day 3 (Sunday):** Polish the UI, run the Pre-Demo Scope Validation Checklist, and practice the judge script.

## Appendices

**Data Lineage Map:**
* **311 Call Volumes & Fallback Info:** Sourced from RVA.gov About RVA 311 page [1].
* **Emergency Guidance:** Sourced from RVA.gov 911 page [3].
* **City Contracts Data:** Sourced from Socrata Open Data Portal (xqn7-jvv2), updated monthly [2].
* **Bid/RFP Award Data:** Sourced from OpenGov portal [5].
* **Exclusion Rules:** Sourced from FAR 9.404 and SAM.gov training materials [6] [7].

## References

1. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
2. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
3. *Getting help through 911 | Richmond*. https://www.rva.gov/911/getting-help-through-911
4. *RVA 311 | AvePoint*. https://www.avepoint.com/case-studies/rva311
5. *Procurement Transparency Dashboard | Richmond - RVA.gov*. https://rva.gov/procurement-services/procurement-transparency-dashboard
6. *9.404 Exclusions in the System for Award Management. | Acquisition.GOV*. https://www.acquisition.gov/far/9.404
7. *Responsibilities/Qualifications (Exclusions)*. https://dodprocurementtoolbox.com/site-pages/responsibility-qualification-exclusions
8. *City of Richmond Department of Procurement Services*. https://www.rva.gov/procurement-services/about-us