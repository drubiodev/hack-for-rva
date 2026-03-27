# Breaking the Silo: Low-Risk Paths to a Citizen-Centric Richmond

## Executive Summary

Municipal governments are fundamentally structured around departments and legacy vendor systems, resulting in a fragmented, high-friction experience for residents. This department-centric architecture is not a bug, but a feature of legacy government design, where local authorities are "fragmented by design" and often procure similar products from a small pool of vendors separately [1]. However, modern policy frameworks, such as the US Office of Management and Budget (OMB) Circular A-11 Section 280, explicitly reframe government services as the primary unit of observation "irrespective of perceived current ownership or budgetary/organizational lines" [2]. 

The financial and experiential costs of this fragmentation are staggering. Evidence from the UK Government Digital Service (GDS) demonstrates that digital transactions are approximately 20 times cheaper than telephone transactions and 50 times cheaper than face-to-face interactions [3]. To capture these savings and improve resident trust, successful cities are moving away from "rip-and-replace" mega-projects. Instead, they are deploying lightweight integration layers—using standards like Open311 and modern iPaaS (Integration Platform as a Service)—to connect existing systems like Dynamics 365, Cityworks, and ArcGIS [4] [5]. 

For Richmond, the path forward requires establishing a "single front door" for residents, backed by observable, governed integrations that route requests across the City's fragmented tech stack (Drupal, Dynamics 365, BizTalk, Cityworks, EnerGov, Oracle RAPIDS). By adopting proven measurement frameworks from GDS, OMB, and the OECD, Richmond can quantify the "silo tax," prioritize high-volume services for integration, and systematically transition to a citizen-centric operating model.

## Problem Context — Department-first structures drive fragmented, high-friction journeys

Government technology architectures historically evolved to serve internal departmental needs rather than holistic resident journeys. Over decades, municipalities accumulated large portfolios of systems, resulting in different solutions per department, separate platforms for finance and HR, and integrations added incrementally as brittle point-to-point connections [5]. The UK's Ministry for Housing, Communities, and Local Government noted a systemic contradiction where local government is "fragmented by design," leading under-resourced teams to separately manage their own local technology stacks of similar products [1].

This fragmentation creates a landscape that few fully understand end-to-end, leading IT leaders to admit they "no longer know exactly how our data flows work" [5]. The consequences for the resident experience include manual handovers, duplicate data entry, delays in service delivery, and lower overall service quality [5]. 

Modern frameworks provide a mandate to break these silos. OMB Circular A-11 Section 280 establishes that "services are the unit of observation for this performance accountability irrespective of perceived current ownership or budgetary/organizational lines" [2]. Similarly, the OECD Digital Government Policy Framework (DGPF) defines "user-driven" and "government as a platform" as core dimensions of a mature digital government [6]. Without a service-centric operating model, Richmond will continue to pay high "friction taxes" in the form of rework and elevated call volumes, ultimately eroding public trust.

## Quantified Impact — Fragmentation inflates costs and lowers satisfaction

Channel and journey fragmentation impose large, measurable cost and experience penalties. Transitioning to a citizen-centric, digital-by-default model yields dramatic financial efficiencies and user satisfaction improvements.

The UK's Digital Efficiency Report and associated SOCITM studies provide stark benchmarks for the cost of government transactions across different channels:

| Transaction Channel | Average Cost per Transaction | Cost Multiplier vs. Digital |
| :--- | :--- | :--- |
| Face-to-face | £8.62 | ~57x more expensive |
| Telephone | £2.83 | ~19x more expensive |
| Digital / Web | £0.15 | Baseline |

*Takeaway: Digital delivery of public services produces a service at least as strong as other channels at a significantly lower unit cost [3].*

Specific service examples further illustrate this delta. For instance, booking a driving test costs £6.62 by post, £4.11 by telephone, but just £0.22 online [7]. By shifting transactional services from offline to digital channels, the UK government estimated potential total annual savings of £1.7 to £1.8 billion [8].

Beyond cost, citizen-centric design measurably improves the user experience. Initial testing of the unified GOV.UK platform compared to previous fragmented sites showed a more positive rating on ease of use (93% compared with 75% before) and speed (80 seconds as opposed to 120 seconds to undertake comparable transactions) [8]. Furthermore, OMB A-11 Section 280 elevates customer experience measures to be of "co-equal importance as traditional measures of financial and operational performance," directly linking a customer's experience to their overall trust in government [2].

## What Successful Governments Changed — One front door plus back-end orchestration

Leaders in digital government have successfully combined a unified "front door" with robust back-end integration and continuous measurement to close the loop from user intent to service fulfillment.

* **Topic and Task Architecture:** Initiatives like GOV.UK reorganized information around user needs and tasks rather than departmental structures, resulting in measurable gains in speed and ease of use [8].
* **311 Ecosystems and Open Standards:** Successful municipalities leverage open standards to connect citizen reporting with operational fulfillment. For example, SeeClickFix 311 CRM provides an Open311 API endpoint, allowing seamless integration of public requests into backend systems [4]. Academic case studies, such as the OpenComm platform using Kansas City's 311 calls, demonstrate how integrating 311 data with external datasets (like Census data) can tackle urban challenges while preserving privacy [9].
* **Life Experiences Coordination:** OMB A-11 Section 280 mandates that agencies proactively coordinate service delivery around "Life Experiences" (e.g., recovering from a disaster or starting a family) to create an integrated, human-centered experience that spans multiple federal programs [2].

To replicate this success, Richmond must pilot a "one cityfront" for top tasks, ensuring that any front-end unification is paired with at least one end-to-end back-end integration (e.g., routing a 311 request directly to a work order system) to prevent the front door from becoming a mere veneer over broken processes.

## Richmond Stack, Mapped to Lightweight Integrations — Quick wins without rip-and-replace

Richmond's technology stack includes Drupal/Acquia (web), AvePoint/Dynamics 365 (311), Microsoft BizTalk (middleware), Trimble Cityworks (DPW work orders), EnerGov/Tyler Technologies (permitting), Oracle RAPIDS (finance/procurement), and ArcGIS (GIS). 

Leading municipalities are not attempting large-scale "rip-and-replace" programs; instead, they are modernizing around existing systems by introducing structured integration layers [5]. 

### Targeted Integrations (60–120 days)
* **Web (Drupal) → 311 (Dynamics 365):** Pre-fill and deep-link from web content directly to request creation.
* **311 (Dynamics 365) → DPW Work Orders (Cityworks):** Utilize Open311-compatible brokerage to route requests and expose status updates back to residents [4].
* **Work Orders/Permitting → ArcGIS:** Use GIS as the authoritative location data source to reduce address errors and surface map-based status updates on the front door.
* **Middleware (BizTalk):** Utilize existing BizTalk infrastructure as a transitional API façade, while planning for modern iPaaS solutions where legacy ESBs struggle with API-first or event-driven patterns [10].

### Integration Approaches Comparison

| Approach | Description | Fit for Richmond | Risks |
| :--- | :--- | :--- | :--- |
| **ESB (e.g., BizTalk)** | Central message bus and orchestration. | Already present; good as a transitional façade. | Struggles with modern API-first and event-driven patterns [10]. |
| **iPaaS** | Cloud-native way to connect legacy and new systems [10]. | Fast time-to-value; provides visual, low-code transparency (e.g., BPMN 2.0) [5]. | Vendor lock-in if overused without governance. |
| **API Gateway + Standards** | Policy, routing, and exposure of consistent APIs (e.g., Open311). | Strong for exposing consistent APIs to external portals. | Does not orchestrate complex workflows by itself. |
| **Event Bus / Webhooks** | Publish/subscribe updates for status changes. | Future-proofing status updates across systems. | Requires strict data model discipline. |

*Takeaway: Richmond should adopt a structured integration layer that allows the City to connect departments without centralizing all data, reducing dependency on brittle point-to-point connections [5].*

## Measurement & Governance — Adopt proven KPIs to price the silo tax

To justify investments and track progress, Richmond must adopt established academic and practitioner frameworks to measure the cost of department-centric architectures versus citizen-centric models.

### Frameworks Alignment

| Framework | Core Metrics / Dimensions | Relevance to Richmond |
| :--- | :--- | :--- |
| **UK GDS Service Manual** | Cost per transaction, completion rate, user satisfaction, digital take-up [11]. | Calculate "as-is" vs "to-be" savings; focus redesign efforts on failure points. |
| **OMB A-11 Section 280** | Trust, Effectiveness, Ease, Efficiency, Transparency, Humanity, Employee Interaction [2]. | Standardize Voice of Customer (VOC); benchmark improvements; inform budget priorities. |
| **OECD DGPF / DGI** | Digital by design, data-driven public sector, government as a platform, open by default, user-driven, proactiveness [6]. | Assess overall digital maturity; justify integration-as-infrastructure and open standards. |

*Takeaway: Richmond should instrument two priority services end-to-end, publishing a quarterly dashboard featuring the GDS 4 KPIs and the OMB A-11 trust metrics to maintain accountability.*

## Risks, Constraints, and Failure Patterns — What to avoid and how to derisk

Government digital transformation initiatives often stall not due to a lack of ambition, but because of legacy integration, fragmented systems, and compliance pressures [5]. 

* **Front Door Veneer:** Launching a unified website without back-end orchestration drives up abandonment and call volumes. Mitigation: Deliver at least one end-to-end integration per release and track journey drop-offs.
* **Point-to-Point Proliferation:** Integrations added incrementally as custom code or undocumented scripts create brittle dependencies and high operational risk [5]. Mitigation: Route flows through an observable integration layer with standardized process modeling (e.g., BPMN 2.0) [5].
* **Consultant Dependency:** Public-sector organizations often struggle to retain integration architecture skills, leading to a recurring risk: "When the consultant leaves, no one really knows how it works" [5]. Mitigation: Require in-house co-delivery, maintain an API catalog, and utilize self-documenting integration platforms.
* **Opaque Automation:** Automation and AI-enabled processes must be transparent by design; automation without transparency does not scale and does not comply [5]. Mitigation: Ensure human-in-the-loop controls and full auditability in the integration layer [5].

## Hackathon vs Systemic Change — What can be shipped in 48 hours vs 6–18 months

**Hackathon Deliverables (48–72 hours):**
* Develop a clickable "one cityfront" prototype for the top 5 resident tasks, featuring deep links to Dynamics 365 (311) and knowledge articles.
* Build a prototype Open311 broker that posts test tickets from a web form into the 311 CRM and echoes the status back to the user.
* Implement a KPI instrumentation starter: track completion rates, drop-offs, and deploy a basic post-transaction trust survey aligned with OMB A-11 wording [2].
* Integrate a GIS-backed address lookup to reduce user errors on forms.

**Requires Systemic Change (3–18 months):**
* Formalize the integration layer (governed APIs, eventing, BPMN-modeled processes) to replace point-to-point scripts [5].
* Establish an Enterprise Voice-of-Customer (VOC) platform and a quarterly CX governance reporting cadence [2].
* Implement a cross-department operating model with designated service owners and shared KPIs.
* Negotiate vendor roadmap agreements for open APIs and webhooks (e.g., with Tyler Technologies and Oracle).

## Roadmap — 0–30–90 days to 12 months

* **0–30 Days:** Select 2 priority services for targeted improvement. Baseline the GDS 4 KPIs (cost per transaction, completion rate, satisfaction, digital take-up) [11] and OMB trust metrics [2]. Stand up an initial API catalog and define the Open311 request mapping to Cityworks.
* **31–90 Days:** Ship version 1 of the front-door interface. Deploy the Open311 to work order integration. Publish the first quarterly CX dashboard. Train internal teams on API standards and process modeling to reduce consultant dependency [5].
* **3–6 Months:** Add GIS-backed status pages for resident transparency. Expand to a second major integration (e.g., reading permit status via EnerGov APIs). Formalize integration governance to prevent point-to-point sprawl. Target a 20-30% reduction in avoidable calls.
* **6–12 Months:** Extend the citizen-centric architecture to 3-5 additional services. Secure vendor commitments for webhooks and API access. Target a 30-50% increase in digital take-up and measurable reductions in the cost per transaction, aligning Richmond's maturity with the OECD Digital Government Index dimensions [6].

## References

1. *Sourcing the stack for local government technology – Technology in government*. https://technology.blog.gov.uk/2025/11/07/sourcing-the-stack-for-local-government-technology/
2. *SECTION 280 – MANAGING CUSTOMER EXPERIENCE ...*. https://bidenwhitehouse.archives.gov/wp-content/uploads/2018/06/s280.pdf
3. *Digital Efficiency Report - GOV.UK*. https://www.gov.uk/government/publications/digital-efficiency-report/digital-efficiency-report
4. *Integrations Overview*. https://www.civicplus.help/seeclickfix/docs/integrations-overview
5. *Why government digital transformation stalls at integration*. https://frends.com/insights/why-government-digital-transformation-stalls-at-integration
6. *The OECD Digital Government Policy Framework (EN)*. https://www.oecd.org/content/dam/oecd/en/publications/reports/2020/10/the-oecd-digital-government-policy-framework_11dd6aa8/f64fed2a-en.pdf
7. *Government transaction costs – the story behind the data – Government Digital Service*. https://gds.blog.gov.uk/2013/01/17/gov-transaction-costs-behind-data/
8. *Government Digital Strategy*. https://assets.publishing.service.gov.uk/media/5a7ba0bfed915d41476219cd/Government_Digital_Stratetegy_-_November_2012.pdf
9. *OpenComm: Open community platform for data integration and privacy preserving for 311 calls - ScienceDirect*. https://www.sciencedirect.com/science/article/pii/S2210670722001858
10. *The Different Types of Integration Platforms*. https://www.alumio.com/blog/4-essential-integration-platforms
11. *Using performance data to improve your service: an introduction - Service Manual - GOV.UK*. https://www.gov.uk/service-manual/measuring-success/using-data-to-improve-your-service-an-introduction