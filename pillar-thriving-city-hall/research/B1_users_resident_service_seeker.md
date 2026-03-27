# Richmond Residents, Real Needs: Designing Plain-Language Service Navigation That Works

## Executive Summary
Richmond's resident service navigation requires an omnichannel, plain-language approach that bridges the digital divide and simplifies complex municipal structures. While web usage is surging, phone channels remain the anchor for service access, and mobile apps are best kept narrowly focused on "on-the-go" tasks. With 9.7% of Richmond residents lacking an internet subscription and the end of federal broadband subsidies, a "web-first" strategy is insufficient on its own. Furthermore, language access must evolve beyond generic machine translation to include live assistance and human-translated core tasks. By designing around four key personas—first-time users, neighborhood reporters, permit seekers, and non-English speakers—Richmond can deploy a guided, top-task-oriented navigation tool that reduces duplicate reports, builds trust through transparency, and ensures equitable access to City services.

## Purpose and Decision Context
Richmond needs a plain-language, omnichannel navigation front door that works for first-time users, neighborhood-issue reporters, permit/licensing seekers, and limited-English proficiency (LEP) residents amid digital divide realities. The goal is to map the user personas and their specific contexts to actionable design implications for a service navigation tool that reduces friction, prevents duplicate requests, and routes users accurately across Richmond's complex multi-agency landscape.

## Richmond Service Navigation Landscape

### Demand and Categories Drive Complexity
RVA311 handles a massive scale of requests, partnering with over 20 different City agencies, including Public Works, Public Utilities, Social Services, and Planning and Development [1]. In 2024, RVA311 provided assistance or supported City partners in responding to over 83,000 requests [1]. This multi-agency structure means residents often face a confusing array of categories, requiring a unified taxonomy that hides the organizational chart from the user.

### Digital Access and Adoption Barriers Persist
Approximately 9.7% of Richmond residents do not have an internet subscription [2]. The federally funded Affordable Connectivity Program (ACP), which offered up to $30 a month for internet services, was discontinued in June 2024 due to a lack of funding [2]. Currently, Lifeline offers discounts up to $9.25 a month for eligible households [2]. Furthermore, relying solely on a smartphone to access the internet has shortcomings, as most wireless plans place caps on monthly data usage [3]. This necessitates low-bandwidth design and the retention of assisted channels.

### Language Access Requires More Than Machine Translation
Currently, RVA.gov uses Google Translate to provide generic translations in 36 languages, accompanied by a disclaimer that it does not substitute the right to obtain a professional translation [4]. In contrast, peer cities like New York provide 311 services via phone in 175 languages and have expanded automated messaging options to 10 designated citywide languages to better serve historically underserved communities [5].

## How Residents Actually Navigate in Peer Cities

### Channel Mix Benchmarks Show Phone and Web Dominance
Data from mid-sized and large cities demonstrates that while web usage is growing rapidly, phone calls remain the dominant channel for 311 services. Mobile apps, while useful, capture a much smaller share of total volume.

| City | Reporting Period | Phone Calls | Web/Online Requests | App/Text/Social Requests | Key Insight |
| :--- | :--- | :--- | :--- | :--- | :--- |
| New York City | FY 2024 | 17.5 million | 18.2 million | ~2.5 million | Web contacts increased 21% over the previous year, matching phone volume, while app/social remains a distinct minority [5]. |
| Sacramento | 2024/25 | 276,058 | 190,483 (combined online/app/email) | N/A (grouped with online) | Phone calls increased by 9.52%, showing that traditional channels are still growing alongside digital adoption [6]. |

*Takeaway:* Design must ensure parity between phone and web channels. The web should serve as the comprehensive catalog, while the phone system requires robust, multilingual IVR routing.

### App Scope Lessons Emphasize "On-the-Go" Focus
Successful 311 apps avoid trying to replicate the entire website. The NYC 311 mobile app provides access to 25 complaint types, whereas the online website provides easy access to 63 common complaint types [7]. NYC's strategy is to add the most important "on-the-go" service requests to the app (like alternate side parking updates) and make it easy for customers to discover the full catalog online [8].

## Personas that Matter

| Persona | Primary Goal | Key Knowledge Gap | Device/Access Context | Primary Risk/Frustration |
| :--- | :--- | :--- | :--- | :--- |
| **A: First-Time User** | Find the right door fast for a simple need (e.g., trash day). | Doesn't know City departments or terminology. | Mobile-first, potentially low-data. | Jargon and dead-ends cause abandonment. |
| **B: Neighborhood Reporter** | Quick report of an issue (pothole, dumping) with status updates. | Unsure of exact category nuances or expected timelines. | Smartphone with camera; spotty data. | Duplicate report blocks without explanation; lack of status updates. |
| **C: Permit Seeker** | Determine correct permit, submit, and pass inspection. | Unaware of sequencing, required documents, and fees. | Mix of desktop (office) and mobile (field). | Circular links, hidden requirements, and repeated rejections. |
| **D: LEP Resident** | Access services with language assistance for comprehension. | Unsure of translation availability or process steps. | Mobile-first; may rely on family assistance. | Machine-only translation with legal disclaimers; no human handoff. |

*Takeaway:* Each persona requires specific design interventions, from guided wizards for permit seekers to location-based deduplication for neighborhood reporters.

### Persona A: First-Time City Service User
* **Goal:** "How do I get X?" (e.g., pay a bill, find trash day).
* **Knowledge:** Knows "City Hall" exists, but not specific departments.
* **Unknowns:** Which department handles the issue, eligibility, timelines.
* **Context:** Mobile-first, potentially using prepaid data.
* **Success/Frustration:** Success is a quick answer in 1-2 steps. Frustration is encountering bureaucratic jargon.
* **Scenario:** "Where do I report a missed trash pickup?" -> First-step question: "What's your address? Is this missed regular pickup or bulk?"

### Persona B: Neighborhood Quality Reporter
* **Goal:** Report an issue (potholes, illegal dumping) and track its resolution.
* **Knowledge:** Vaguely aware of 311.
* **Unknowns:** What constitutes a City vs. private issue; expected repair timelines.
* **Context:** Smartphone only, uses photos to document issues.
* **Success/Frustration:** Success is easy photo/location intake and immediate ticket status. Frustration is opaque timelines and duplicate reporting hurdles.
* **Scenario:** "Report pothole" -> First-step question: "Use location; is it on a City street? Upload photo."

### Persona C: Permit and Licensing Seeker
* **Goal:** Determine the correct permit, submit plans, and pass inspections.
* **Knowledge:** Knows Planning and Development Review (PDR) exists; has some prior experience.
* **Unknowns:** Specific permit types, required documents, fees, and sequencing.
* **Context:** Desktop for uploading plans, mobile for checking status in the field.
* **Success/Frustration:** Success is an unambiguous mapping to the right permit with a tailored checklist. Frustration is circular links and hidden requirements.
* **Scenario:** "Add a deck" -> First-step question: "Are you changing the structural footprint? Are you a contractor or the owner?"

### Persona D: Non-English-Speaking Resident
* **Goal:** Access services and understand rights/eligibility.
* **Knowledge:** Relies on community hearsay; limited formal understanding of City processes.
* **Unknowns:** Translation availability, process steps, and rights.
* **Context:** Mobile-first; mixed literacy; may have a family member assist.
* **Success/Frustration:** Success is a visible language toggle and "request interpreter" option. Frustration is generic machine translation that fails to convey nuance.
* **Scenario:** "Noise complaint" -> First-step question: Language select -> "Is it recurring? Immediate danger?"

## First-Step Question Framework
To reduce cognitive load, the navigation tool should use a branching, plain-language question framework that routes users without requiring department knowledge.
* **Where?** (Address, is it on a City right-of-way?)
* **What changed/happened?** (Repair vs. new work; missed pickup vs. illegal dumping)
* **Who is requesting?** (Resident, contractor, business owner)
* **When/Urgency?** (Is it a safety risk? Is it recurring?)

## Design Implications for a Plain-Language Navigation Tool

### Content and Information Architecture
Municipal homepages should avoid overcrowding and clearly communicate purpose upfront [9]. Navigation should feature an organized menu bar with four to six prominent options and specific calls to action (CTAs) like "Pay Your Water Bill" rather than generic "Learn More" links [9]. Content must be written in plain language, defined as communication the audience can understand the first time they read or hear it [10] [11].

### Search and Taxonomy
Because not all users navigate via menus, a prominent in-site search capability is essential [9]. The taxonomy should map resident vocabulary (e.g., "dumping") to official terms ("illegal solid waste").

### Multilingual Experience
Relying solely on Google Translate is insufficient. The City should publish core tasks in the top 5-8 local languages using human translation and integrate a "press for interpreter" option in the 311 IVR system, mirroring successful expansions in cities like New York [5].

### Mobile and Low-Bandwidth Design
Given that 9.7% of residents lack internet subscriptions and many rely on data-capped smartphones [2] [3], the digital tool must be lightweight. Pages should load quickly on 4G, and forms should support save-and-resume functionality.

### Status and Transparency
Trust rises when status is centralized and timely. Outage maps and status trackers should provide centralized, actionable details written in simple language, prioritizing estimated restoration times and indicating when the data was last updated [12]. RVA311's privacy policy, which hides personally identifiable information from public view while allowing anonymous submissions, should be clearly communicated to build trust [1].

### Duplicate Prevention
RVA311 asks residents to avoid submitting duplicate requests for common issues like potholes and streetlights, making it easy to check existing reports [1]. The new tool should auto-scan for nearby open reports using location data and prompt users to "join" an existing request rather than creating a new one.

### Cross-Agency Routing
RVA311 partners with over 20 different City agencies [1]. The navigation tool must feature an "I don't know the department" path with smart routing rules that assign tickets to the correct agency on the backend, providing a consolidated status view for the user.

### App Scope Control
To keep the app simple and highly rated, it should focus on the most important "on-the-go" service requests (like reporting a pothole or checking trash schedules) and direct users to the website for the full catalog of complex services like permits [8].

## Risks, Failure Cases, and Mitigations
* **Machine Translation Misleads:** Generic translation can erode trust. *Mitigation:* Translate curated top tasks professionally and provide clear pathways to live interpreters.
* **App Bloat:** Adding too many categories to the app makes it unusable. *Mitigation:* Enforce strict "mobile-scope" guardrails; route complex tasks to the web [7].
* **Web-Only Exclusion:** Digital-only solutions ignore the 9.7% offline population [2]. *Mitigation:* Maintain robust phone support and partner with community organizations for assisted access.
* **Status Opacity:** Users call back when they don't see progress. *Mitigation:* Always display "last updated" timestamps and clear stage indicators [12].

## Measurement Plan and Targets
To prove the tool works, Richmond should track:
* **Task Completion Rate:** Target a 15% increase for the top 10 tasks within 6 months.
* **Call Deflection:** Target a 20% increase in web deflection for top-info queries without spiking abandonment rates.
* **Duplicate Report Rate:** Target a 25% reduction per 1,000 residents through location-based pre-checks.
* **LEP Engagement:** Target a 30% increase in sessions using translated pages or interpreter services.

## Pilot and Rollout Roadmap
* **Phase 1 (0-30 days):** Align data baselines, select the top 5 tasks, draft plain-language content, and prototype the first-step wizard.
* **Phase 2 (31-60 days):** Develop multilingual pages for top tasks, implement IVR interpreter routing, add "last updated" status stamps, and conduct a soft launch.
* **Phase 3 (61-90 days):** Deploy duplicate pre-checks, launch community outreach programs (libraries, faith groups), publish a public performance dashboard, and iterate based on feedback.

## References

1. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
2. *Richmond City Council wants to increase internet speeds, close ‘digital divide’ • Virginia Mercury*. https://virginiamercury.com/2024/09/17/richmond-city-council-wants-to-increase-internet-speeds-close-digital-divide/
3. *Closing the Digital Divide | Richmond Fed*. https://www.richmondfed.org/publications/research/econ_focus/2020/q2-3/feature2
4. *Permits and Inspections | Richmond*. https://www.rva.gov/planning-development-review/permits-and-inspections
5. *office of technology and innovation - 311 customer service ...*. https://www.nyc.gov/assets/operations/downloads/pdf/mmr2024/311.pdf
6. *City’s 311 Customer Service Center sees growth, faster response times in annual report - Sacramento City Express*. https://sacramentocityexpress.com/2025/10/20/citys-311-customer-service-center-sees-growth-faster-response-times-in-annual-report/
7. *311 Services - Data Team - New York City Council*. https://council.nyc.gov/data/311-services/
8. *Secrets Behind Successful 311 Apps: Unlocking User Satisfaction*. https://www.govtech.com/biz/data/secrets-behind-successful-311-apps-unlocking-user-satisfaction
9. *Municipal Homepage Design Best Practices: Creating User-Friendly Experiences*. https://www.govstack.com/resources/posts/municipal-homepage-design-best-practices-creating-user-friendly-experiences/
10. *Our plain language approach and resources | U.S. Department of Labor*. https://www.dol.gov/agencies/eta/ui-modernization/use-plain-language/our-approach
11. *Plain language | Portland.gov*. https://www.portland.gov/officeofequity/digital-accessibility/how-make-accessible-web-content/plain-language
12. *A Lesson on Top Tasks from Hurricane Beryl - NN/G*. https://www.nngroup.com/articles/top-tasks/