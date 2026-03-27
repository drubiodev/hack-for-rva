# This Helps X Do Y: City Hall Demo Framing That Wins Trust

## Executive Summary
The most effective civic tech demo language is concrete, user-centered, and honest. Vague promises of "efficiency" or "AI magic" fail to build trust with municipal stakeholders who understand the deep complexities of their operations. Precision beats promises: you must name the specific user, the exact task, the named dataset, and the current pain point. 

Crucially, every demo must include a "without" clause to establish guardrails. For example, the federal government-wide FOIA request backlog surpassed 200,000 requests for the first time in FY 2022 [1]. A tool cannot magically erase statutory review timelines, but it can help requesters find previously released records. Similarly, while 311 data can be used to reduce rat complaints by more than 60 percent (as seen in Somerville), relying solely on 311 data without accounting for demographic usage gaps can exacerbate inequalities [2]. By explicitly stating what a tool *does not* do—such as "without replacing staff judgment" or "without changing routing priorities"—you de-risk the pitch and prove you understand the realities of local government.

## What "This Helps X Do Y" Looks Like in City Hall
Winning demo language relies on a single, actionable sentence that names the user, task, dataset, current pain, and a guardrail. 

**The Formula:**
"This helps [user] [do specific task] [using specific data/approach], instead of [current approach], without [overclaiming what it does]."

## Problem-Type Playbooks

### 311 Service Navigation & Category Selection
Research shows that 311 usage varies by neighborhood, and relying solely on it can exacerbate inequalities if affluent households are overrepresented [2]. Framing must reflect equity realities and focus on cutting misroutes, not "auto-fixing" 311.

* This helps a resident who reports a pothole find the correct 311 category in under 60 seconds, using your city’s 311 API labels and historical misroute patterns, instead of guessing from a 40+ item dropdown and getting re-routed—without changing request priority or auto-submitting tickets.
* This helps a Spanish-speaking caller match "basura ilegal" to "illegal dumping" in plain language, using multilingual synonyms from past 311 submissions, instead of navigating English-only pages—without making service time guarantees.
* This helps a neighborhood association share the top 5 related categories near their address, using geo-tagged 311 data from the open data portal, instead of hunting across department pages—without implying official City endorsement.
* This helps a resident check if a reported streetlight outage is already in the system, using recent 311 cases near their block, instead of submitting duplicates—without closing any cases or merging reports.
* This helps residents preview typical resolution steps and timelines for their category, using published SLA descriptions, instead of calling the hotline for basic status—without overriding agency SLAs or staff judgment.
* This helps a community group spot under-reported issues by comparing 311 rates to neighborhood population, using open demographic data, instead of assuming equal usage—without reweighting priorities or allocation decisions.

### Procurement & Contract Management
In New York City, the PASSPort system manages every stage of procurement, but delays in contract registration and public hearings can undermine public faith [3]. Frame tools as early-warning systems, not automated risk adjudicators.

* This helps procurement staff see contracts expiring in the next 60–90 days, using your public contract registry or PASSPort export, instead of rebuilding pivot tables each month—without rating vendor risk or altering workflows.
* This helps program managers track required public hearing notices due this month, using PPB rule deadlines and PASSPort milestones, instead of calendar scrambles—without scheduling hearings or speaking for agencies.
* This helps finance teams flag contracts missing funding allocations, using FMS budget lines linked to PASSPort IDs, instead of chasing emails across departments—without moving funds or approving budgets.
* This helps vendor liaisons identify awards stuck at a specific step for 30+ days, using stage timestamps from PASSPort, instead of guessing where packages are stalled—without escalating or adjudicating exceptions.
* This helps compliance teams surface sole-source items awaiting notices, using the City Record/Open Data feeds, instead of manual cross-checks—without certifying compliance.
* This helps CPOs see average days-in-stage for top agencies, using PASSPort logs, instead of anecdotal reports—without setting or enforcing time limits.

### Building Permits & Inspections
Permit backlogs frustrate developers, as seen in Baltimore [4]. However, modernizing systems works: Tacoma saved nearly 30 hours a month processing over-the-counter permits and an additional 44 hours a month by offering ePermits through Accela [5]. 

* This helps a homeowner see exactly which submittals are still missing for a deck permit, using Accela/EnerGov permit checklists, instead of calling three counters—without guaranteeing approval or code interpretations.
* This helps a contractor find the earliest inspection window for the week, using inspector availability from the permitting system, instead of phone tag—without booking or reprioritizing inspections.
* This helps plan reviewers share standard completeness check feedback, using past correction codes and open datasets, instead of bespoke emails—without issuing determinations.
* This helps applicants track permit status changes by step, using Accela/EnerGov status history, instead of daily portal refreshes—without expediting reviews.
* This helps permit managers spot applications idle 15+ days between steps, using timestamp analytics, instead of ad-hoc backlog hunts—without reassigning staff.
* This helps residents see neighborhood permitting activity totals, using open permit data, instead of FOIA requests—without predicting individual project outcomes.

### HR & Hiring (Civil Service)
The civil service system is often slow and cumbersome, leading to prolonged delays in hiring [6]. Show pipeline visibility rather than promising rule changes.

* This helps HR see time-from-requisition-to-offer by stage, using civil service transaction data (e.g., Data.gov hiring datasets), instead of manual spreadsheets—without changing exam rules or eligibility lists.
* This helps recruiters auto-surface eligible list candidates nearing expiration, using list expiry dates, instead of last-minute scrambles—without skipping required order-of-list calls.
* This helps hiring managers preview typical timelines by classification, using historical medians, instead of guesswork—without promising faster appointments.
* This helps applicants check their application status by step, using the job portal feed, instead of inbox uncertainty—without ranking candidates or giving legal advice.
* This helps HR spot background check queues >10 days, using vendor turnaround data, instead of anecdotal complaints—without intervening with providers.
* This helps workforce planners map vacancy hotspots, using filled-vs-authorized positions, instead of quarterly slide decks—without reclassifying roles.

### Budget & Spending (Open Checkbook)
Cities like Atlanta use Open Checkbook portals to provide transaction-level detail on goods and services purchased [7]. Focus on payment search and visibility.

* This helps a resident find all FY25 payments to Vendor X in minutes, using Open Checkbook/ERP open data, instead of filing a records request—without asserting audit findings.
* This helps a reporter compare capital outlays vs. prior year, using spending categories, instead of custom queries—without interpreting policy variance.
* This helps a council aide see top 10 payees in their department last quarter, using transaction-level data, instead of emailing Finance—without rating vendor performance.
* This helps budget analysts export filtered spend for a committee briefing, using built-in CSV exports, instead of re-cutting reports—without reconciling to CAFR totals.
* This helps procurement cross-check encumbrances vs. payments, using PO linkages, instead of duplicate lookups—without certifying balances.
* This helps small vendors see average payment cycle times, using check-issue dates, instead of assumptions—without committing to payment timelines.

### Public Records/FOIA
With government-wide FOIA backlogs surpassing 200,000 requests in FY 2022 [1], portals like NYC's OpenRecords help centralize requests [8]. Frame tools around duplicate reduction and expectation setting.

* This helps requesters find previously released records before they file, using OpenRecords/portal search, instead of duplicating asks—without providing legal advice.
* This helps FOIA staff spot duplicate or overlapping requests by keyword/agency/date, using portal metadata, instead of manual inbox scans—without denying or merging requests automatically.
* This helps journalists track where their request sits in the queue, using status timestamps, instead of weekly check-ins—without expediting statutory timelines.
* This helps agencies pre-publish high-demand records (e.g., contracts), using "release to portal" features, instead of one-off emails—without redaction decisions.
* This helps residents estimate likely turnaround ranges by record type, using historical medians, instead of vague expectations—without committing to deadlines.
* This helps requesters pick the right agency the first time, using portal routing guidance, instead of misdirected filings—without submitting on their behalf.

### Council Agendas & Legislation
City clerks face immense pressure managing agendas, minutes, and hybrid meetings [9]. Systems like Legistar (used by NYC and Philadelphia) centralize this data [10] [11]. 

* This helps a resident see what Council will vote on this week, using Legistar calendar feeds, instead of combing PDFs—without being an official record.
* This helps staff compile all artifacts (agenda, minutes, video) in one place, using agenda management links, instead of multi-tab searches—without hosting or altering records.
* This helps advocates set alerts for new items tagged to a topic, using Legistar tags, instead of manual refreshes—without guaranteeing completeness.
* This helps councilmembers review late-filed agenda changes, using change logs, instead of email threads—without version adjudication.
* This helps constituents find how their member voted last session, using roll-call data, instead of FOIA—without summarizing positions.
* This helps clerks estimate packet prep time by agenda size, using historical averages, instead of guesswork—without changing deadlines.

### Capital Projects Status
Cities provide transparency through dashboards, such as NYC's Capital Projects Dashboard (updated three times per year) [12], San Diego's CIP tools [13], and Charlotte's quarterly-updated dashboard [14]. 

* This helps a council office see projects in their district with current phase and projected completion, using the City’s capital dashboard (e.g., updated 3x/year), instead of emailing PMs—without asserting real-time accuracy.
* This helps residents locate nearby projects on a map, using the city’s CIP map viewer, instead of PDF lists—without interpreting detours or closures.
* This helps PMOs spot projects slipping quarters, using phase timestamp deltas, instead of ad-hoc updates—without reprioritizing portfolios.
* This helps budget staff compare commitments vs. spends, using FMS/ERP capital lines, instead of manual rollups—without authorizing reprogramming.
* This helps communications teams pre-brief neighborhoods on milestones due next month, using schedule extracts, instead of last-minute notices—without promising dates.
* This helps watchdogs see plan/design/construction counts by department, using dashboard summaries, instead of FOIA—without performance grading.

### Code Enforcement & Property Violations
Code enforcement agencies often struggle with backlogs; a King County audit found that almost a third of cases opened between 2015 and 2022 were high risk, yet the backlog continued to grow due to a lack of prioritization [15]. 

* This helps code enforcement triage incoming complaints by risk, using violation history and parcel data, instead of first-in-first-out—without making enforcement decisions.
* This helps residents see what happens after they report an issue, using published process steps, instead of uncertainty—without promising response times.
* This helps supervisors spot cases idle >30 days, using case timestamps, instead of manual case checks—without reassigning inspectors.
* This helps property owners see required corrective actions for common violations, using standard notice templates, instead of repeated calls—without legal advice.
* This helps neighborhood groups visualize enforcement activity over time, using open violation data, instead of FOIA—without implying enforcement completeness.
* This helps managers identify communication gaps, using link-outs to improved guidance, instead of back-and-forth—without altering notices.

### Business Licensing & Renewal
High volumes of applications can cause severe delays, as seen when the City of Dothan had to alert business owners to processing delays and pause penalties through the end of February 2026 [16]. 

* This helps business owners see their renewal deadline and grace periods, using licensing database dates, instead of calling City Hall—without waiving fees or penalties.
* This helps owners confirm which documents are missing for renewal, using checklist rules by license type, instead of trial-and-error uploads—without submitting on their behalf.
* This helps city staff flag pending renewals 15 days from penalty dates, using status dashboards, instead of inbox triage—without granting extensions.
* This helps entrepreneurs choose the right license type, using plain-language descriptions mapped to SIC/NAICS, instead of misapplication—without legal or tax advice.
* This helps chambers of commerce share renewal calendars with members, using exportable date feeds, instead of manual newsletters—without official City status.
* This helps compliance teams spot duplicate applications, using owner and location matching, instead of line-by-line reviews—without application decisions.

## Common Framing Mistakes and How to Fix Them

| Mistake (Bad Line) | Why it Fails | Fix (Better Line) |
| :--- | :--- | :--- |
| "This fixes 311 and routes requests automatically." | Overclaims power; ignores bias and SLA reality. | "This helps a resident pick the right 311 category in under 60 seconds, using the city’s 311 API and plain-language labels, instead of guessing and being re-routed—without changing routing or priorities." |
| "This automates procurement risk management." | Implies policy decisions and liability. | "This turns the public contract registry into an early-warning dashboard for contracts expiring in 60–90 days, instead of monthly spreadsheet rebuilds—without rating vendor risk or altering workflows." |
| "This improves permitting." | Vague; no user, task, data, or pain. | "This helps a contractor see missing submittals and schedule prerequisites from Accela/EnerGov data, instead of phone tag—without guaranteeing approvals." |
| "This streamlines FOIA." | Overpromises speed; legal risk. | "This helps requesters find posted records and similar requests in the portal before filing, instead of duplicating asks—without expediting legal review." |
| "This is a council agenda tool." | Underdescribes; no user, task, or dataset. | "This helps residents see what Council will vote on this week, using Legistar feeds, instead of combing PDFs—without being the official record." |
| "This tracks capital projects in real time." | Misleads on cadence. | "This shows district projects with phase and budget from the city’s capital dashboard, updated quarterly/3x-year—without asserting real-time accuracy." |

*Takeaway: Most mistakes either overclaim outcomes or underdescribe the user, task, and dataset.*

## Opening Sentence Options for the Demo Pitch
Start with "who/what/how" in one breath—then show it.

* We built small helpers that use your city’s own data to make one painful task faster—for residents and staff—without replacing judgment.
* In 60 seconds, here’s how a resident can find the right 311 category using your open data—no AI magic, just plain language.
* This is a contract early-warning view from your registry export: what needs attention in the next 60–90 days—no risk scores, just dates.
* If you manage permits, this shows missing submittals and next steps from Accela—no promises on timelines, just clarity.
* Residents ask "what’s Council voting on this week?"—we answer that from Legistar, not from PDFs.
* FOIA teams: here’s how we cut duplicates using your portal’s own records—no change to legal review.
* Capital projects, by district, with the update cadence right on screen.
* We’ll say the dataset and what we don’t do on every screen.

## Evidence & Sources to Name On-Screen

| Problem Type | Dataset/System to Name | Example Cities/Notes |
| :--- | :--- | :--- |
| 311 Navigation | 311 API / Open Data service request table | GovTech notes usage/bias risks; tie to plain-language labels [2]. |
| Procurement | Contract registry/PASSPort export; City Record | NYC Comptroller details pipeline delays [3]. |
| Permitting | Accela/EnerGov permit and inspection exports | Tacoma saved 30 + 44 hours/month [5]; Baltimore backlog [4]. |
| HR/Hiring | Civil service/job action datasets; ATS portal feeds | Data.gov "City Jobs Hiring Data" [17]; ICMA on slow civil service [6]. |
| Budget/Spend | Open Checkbook / ERP open data (e.g., Tyler) | Atlanta’s Open Checkbook shows transaction-level spend [7]. |
| FOIA | OpenRecords/FOIA portal search and status | NYC OpenRecords [8]; GAO cites 200k+ backlog FY22 [1]. |
| Agendas | Legistar/Granicus agenda management feeds | NYC Council [10] and Philadelphia [11] Legistar calendars. |
| Capital Projects | Capital dashboards (Power BI/ArcGIS) + FMS | NYC (updated 3x/year) [12], San Diego CIP [13], Charlotte [14]. |
| Code Enforcement | Open violation data; parcel data; audit references | King County audit: growing backlog, need prioritization [15]. |
| Licensing | Business license database exports; renewal calendars | Dothan publicly announced renewal delays and penalty pauses [16]. |

*Takeaway: Cite the exact dataset/system so stakeholders trust the demo.*

## Risk Guardrails You Should Say Out Loud
Prevent misinterpretation with explicit "without" statements:
* Without replacing staff judgment, legal review, or official records.
* Without guaranteeing timelines, approvals, or prioritization.
* Without changing routing, SLAs, or agency workflows.
* Without asserting real-time accuracy beyond the dataset’s update cadence.
* Without claiming City endorsement; this is a community-built helper using public data.

## Quick Test Before You Demo
If a line fails any check, rewrite it:
1. Can a non-technical staffer identify the user, task, dataset, and current pain in 10 seconds?
2. Is there a clear "without" clause that prevents the top misinterpretation?
3. Does the line reference a specific, real dataset or system by name?
4. Could a skeptical auditor verify the claim using public info?
5. Would a resident or staffer hear this and know exactly when they’d use it tomorrow?

## References

1. *FOIA Backlogs Hinder Government Transparency and Accountability | U.S. GAO*. https://www.gao.gov/blog/foia-backlogs-hinder-government-transparency-and-accountability
2. *Cities Using 311 Data in Novel Ways Discover Drawbacks*. https://www.govtech.com/data/Cities-Using-311-Data-in-Novel-Ways-Discover-Drawbacks.html
3. *
  NYC Contracts - Office of the New York City Comptroller
Mark Levine*. https://comptroller.nyc.gov/reports/nyc-contracts/
4. *Developers frustrated over backlog for Baltimore City permits*. https://www.wbaltv.com/article/baltimore-permit-backlog-developers-frustrated/69123032
5. *Improving The Permit Process – A Quest to Hear The ...*. https://www.accela.com/wp-content/uploads/2022/08/Accela-Tacoma-CaseStudy-005.pdf
6. *Tackling the Local Government Talent Shortage | icma.org*. https://icma.org/articles/pm-magazine/tackling-local-government-talent-shortage
7. *Checkbook | City of Atlanta*. https://www.atlantaga.gov/i-want-to/open-checkbook
8. *Home - OpenRecords - NYC.gov*. https://a860-openrecords.nyc.gov/
9. *Common pain points for city clerks and how technology can help*. https://www.diligent.com/resources/blog/pain-points-clerks-technology-help
10. *The New York City Council - Calendar - NYC.gov*. https://legistar.council.nyc.gov/
11. *
	City of Philadelphia - Calendar
*. https://phila.legistar.com/calendar.aspx
12. *NYC Capital Projects Dashboard*. https://www.nyc.gov/site/capitalprojects/index.page
13. *CIP Project Information | City of San Diego Official Website*. https://www.sandiego.gov/cip/project-info
14. *Capital Projects Dashboard - City of Charlotte*. https://www.charlottenc.gov/Growth-and-Development/Projects/Capital-Projects-Dashboard
15. *Growing Case Backlog Requires Re-prioritization of Code Enforcement Resources - King County, Washington*. https://kingcounty.gov/en/independents/governance-and-leadership/government-oversight/auditors-office/reports-papers/reports/2023/code-enforcement
16. *📢The City of Dothan is alerting business owners to delays ...*. https://www.facebook.com/wiregrassdailynews/posts/the-city-of-dothan-is-alerting-business-owners-to-delays-in-processing-business-/781533024985328/
17. *City Jobs Hiring Data - Dataset - Catalog*. https://catalog.data.gov/dataset/city-jobs-hiring-data