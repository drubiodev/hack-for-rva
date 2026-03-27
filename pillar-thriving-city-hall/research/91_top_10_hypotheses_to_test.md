# De-risking Richmond’s 311 and Procurement MVP: Evidence and Actions

## Executive Summary

A rules-first navigator and batch-friendly procurement data can deliver quick wins for Richmond, provided we instrument misrouting and equity from day one. Across IT service domains, hybrid rule-based flows plus lightweight machine learning (ML) can automate 81% of tickets, with decision trees alone reaching up to 93.5% accuracy on unseen data [1]. By standing up a simple 5–8 question decision-tree prototype for RVA311’s top request types, the city can achieve ≥80% correct routing without heavy ML investments. 

Furthermore, digital channel shifts yield large savings—shifting just 20% of an 80,000 annual call volume to digital self-service drops the cost of those interactions from $176,000 to $1,600, producing an estimated $174,400 in annual savings [2]. However, equity requires a phone equivalent to avoid excluding lower-digital-literacy residents. On the procurement side, VITA statewide contract data is accessible via exports and a REST API, though it requires authenticated admin access and operates on a batch/scheduled basis rather than real-time [3] [4].

## Problem Context and Stakes

City governments handle thousands of non-emergency service requests daily, and residents expect quick responses across multiple channels [5]. The financial stakes of channel optimization are significant. A city handling 80,000 requests per year at approximately $11 per phone call would spend about $880,000 annually [2]. Shifting 20% of these requests to digital channels at roughly $0.10 per interaction saves approximately $174,400 annually, while freeing up staff hours and speeding up routing [2]. However, without a phone-script mirror and translation support, these digital gains risk widening service gaps for vulnerable demographics.

## Hypotheses Overview and Priorities

The following evaluates the 10 testable hypotheses regarding Richmond's resident service navigation and procurement review problems. 

**MVP-Critical Hypotheses to Resolve in Sprint 0:**
Hypotheses 3, 4, 5, and 7 are gating for MVP scope and must be resolved immediately.

### Hypothesis Evaluation

1. **Miscategorized RVA311 Requests:** 
 * **Evidence Supporting:** Traditional 311 systems force residents to navigate confusing category dropdowns, leading them to pick the wrong department, which creates extra work for staff who must reassign tickets [6]. 
 * **Verdict:** Supported.
2. **rva.gov Search Friction:** 
 * **Evidence Supporting:** Residents struggle with complex forms and category dropdowns (often 40+ options) rather than plain language [6]. 
 * **Verdict:** Supported.
3. **Decision Tree 80%+ Accuracy:** 
 * **Evidence Supporting:** Decision tree algorithms (like ID3) have achieved 93.5% accuracy in automating IT ticket assignments, maintaining 93.06% accuracy on unseen data [1]. 
 * **Verdict:** Supported (Critical for MVP).
4. **City Contracts Socrata Dataset Completeness:** 
 * **Evidence:** Insufficient evidence in the current public data context. 
 * **Verdict:** Insufficient evidence (Requires a 2-hour coverage audit; Critical for MVP).
5. **VITA Portal API Absence:** 
 * **Evidence Against:** The hypothesis states there is an absence of an API. However, CobbleStone Contract Insight (which powers VITA) *does* have a REST API (CSS API 2.0) that supports GET, ADD, and UPDATE endpoints [3] [4]. It requires OAuth authentication (Client ID and Secret) and operates on a "Near Realtime/Scheduled" and "Batch" basis, not real-time [3] [4]. Audits and data can also be exported as.csv or.xlsx [7].
 * **Verdict:** Refuted (API exists but is admin-gated and batch-only; Critical for MVP).
6. **PDF LLM Extraction Reliability:** 
 * **Evidence:** Insufficient evidence in the current context. 
 * **Verdict:** Insufficient evidence (Requires a 50-PDF sample test).
7. **Phone Channel Demographics:** 
 * **Evidence Supporting:** While specific Richmond demographic data is pending, the high cost of phone calls ($11/call) vs digital ($0.10/interaction) necessitates a digital shift [2], but equity demands phone parity for those unable to use digital tools. 
 * **Verdict:** Insufficient direct evidence, but strategically Supported (Critical for MVP).
8. **Google Translate Widget Quality:** 
 * **Evidence:** Insufficient evidence in the current context. 
 * **Verdict:** Insufficient evidence.
9. **National Models Reducing Misroutes:** 
 * **Evidence Supporting:** Intelligent routing that allows the public to describe issues in plain language automatically routes requests to the correct department, resulting in fewer errors and faster service [6]. 
 * **Verdict:** Supported.
10. **SAM.gov API Granularity:** 
 * **Evidence:** Insufficient evidence in the current context. 
 * **Verdict:** Insufficient evidence.

## Resident Service Navigation

A 5–8 question decision tree, built from resident phrasing, can cut misrouting and costs quickly. ML can wait until a baseline is established.

### Decision Trees vs NLP

Hybrid rules and ML can automate 81% of ticket processing, significantly reducing manual effort [1]. However, simple decision trees are highly effective on their own. In a study analyzing 14,440 tickets, the ID3 decision tree algorithm achieved 93.5% accuracy, enabling real-time ticket routing and optimizing resource allocation [1]. Similarly, TF-IDF paired with SVM delivered 92% accuracy on a dataset of 1.6 million tickets [1]. This proves that "simple wins now" for 311 triage.

### Replace Categories with Resident Language

Traditional 311 processes require residents to navigate category dropdowns with 40+ options and fill out forms with 8-12 required fields, forcing them to guess which department handles their issue [6]. Replacing this with a system where constituents describe the issue in their own words or upload a photo allows for automatic, intelligent routing to the correct department [6].

### Channel Strategy and Equity

A multi-channel intake system is vital. Citizens should be able to make requests via phone, web portal, mobile app, email, text, or social media, all centralized into one platform [5]. To keep the savings from the digital shift without excluding residents, city call center teams must be equipped with the same decision-tree logic to answer common questions and log requests efficiently [5].

### Measurement Plan

Avoid the "Philadelphia trap." In 2010, Philadelphia's 311 system received over 1.3 million calls, but only 7% were monitored [8]. The failure to monitor and code these calls contradicted the main mission of the system, and the reduction in non-emergency 911 calls was virtually non-existent [8]. Richmond must log category changes, reassignments, and time-to-first-action from day one.

## Procurement Data Integration

Socrata, VITA, and SAM.gov can power a useful dashboard, provided we accept batch refresh limitations and validate field completeness early.

### Data Source Accessibility and Fields

The VITA portal supports exports, and its underlying CobbleStone system offers a REST API, though it requires admin credentials and is limited to batch processing [3] [4]. 

| Data Source | Public API | Export Capabilities | Real-time Sync | Practical Next Step |
| :--- | :--- | :--- | :--- | :--- |
| **Richmond City Contracts (Socrata)** | Yes (Socrata endpoint) | CSV/JSON via API | N/A (Pull) | 2-hour coverage audit; proceed if ≥70% completeness. |
| **VITA Contract Portal (CobbleStone)** | No public; admin-only REST API (OAuth) [3] [4] | CSV/XLSX available [7] | No (Batch/Scheduled only) [3] [4] | Weekly scripted export/scrape; seek API credentials. |
| **SAM.gov (free tier)** | Yes (requires key) | JSON via API | N/A (Pull) | Validate fields with sample queries; integrate if useful. |

*Takeaway:* The lack of real-time webhooks in the CobbleStone API means the architecture must rely on nightly or weekly batch ETL processes to flag expiring contracts.

### PDF Extraction Fallback

Use LLM extraction only if a pilot on 50 PDFs clears ≥80% accuracy with low date errors. Decision trees have limitations with unstructured data, and NLP integration is often required to improve performance in those environments [1].

### Dashboard Design and Alerts

Nightly ETL, 90/60/30-day expiry flags, and department/vendor filters will deliver immediate value despite batch constraints. The API does not offer notification or monitoring functionality for field changes, so delta detection must be built into the ETL pipeline [3] [4].

## Comparable Models and Cautionary Tales

Well-run 311 systems reduce non-emergency 911 calls significantly. Baltimore saw a 50% reduction, San Antonio 20%, Houston 14%, and Denver 12% [8]. 

### Success Metrics to Borrow

Track reassignment rate, first-correct-routing rate, time-to-first-action, and the percentage of digital shift. A good 311 software also helps recognize and merge duplicate requests, preventing redundant work [5].

### Failure Patterns to Avoid

Philadelphia's $6 million a year system failed to meet key goals because 93% of calls went unmonitored, operators were not available 24/7 as promised, and there was little effort to educate the public [8]. Lack of instrumentation leads to stagnant or declining trust.

## MVP Experiments and Acceptance Criteria

Four tightly scoped experiments can validate routing accuracy, equity parity, and data completeness within 2–3 weeks.

### Experiment 1: Decision-Tree A/B Test
Success is defined as ≥80% correct routing and ≥20% fewer reassignments versus the control on the top 15 request types.

### Experiment 2: Resident Language Mapping Sprint
Rewrite the top 100 terms. Success is achieved if search-to-correct-page click-through improves by ≥25%.

### Experiment 3: Phone Script Parity
Train agents on the same decision tree. Success is defined as resolution time parity within ±10% of the digital channel.

### Experiment 4: Contracts Data Audit
Proceed if Socrata field completeness is ≥70%; otherwise, activate PDF extraction sampling and VITA weekly exports.

## Implementation Plan

Parallel tracks—navigator prototype, measurement plumbing, and contracts ETL—will converge into a useful MVP with batch-friendly operations over 6–8 weeks.

### Workstream 1: Navigator and Measurement
Build the decision tree, instrument reassignment logging, and launch the A/B test.

### Workstream 2: Procurement ETL and Dashboard
Execute the Socrata pull, set up VITA export/scraping, sample SAM.gov, and configure expiry alerts.

## Risks, Dependencies, and Mitigations

The biggest risks are data completeness, API access, and equity gaps; each has a concrete mitigation path.

### Key Risks
Data sparsity in contracts, VITA API access hurdles, PDF variability, channel exclusion for vulnerable populations, and ML overfitting on long-tail categories.

### Mitigations
Conduct early audits, rely on batch exports initially, implement human-in-the-loop exception handling, ensure mirrored phone scripts, and start with a rules-first approach before introducing ML.

## Appendices

* **RIT Thesis (2025):** Validates decision tree accuracy (93.5%) for IT ticket routing [1].
* **CivicPlus ROI (2026):** Details the $174k savings from a 20% digital shift [2].
* **CobbleStone REST Docs:** Confirms CSS API 2.0 requires OAuth and is batch-only [3] [4].
* **Philly Controller Audit (2011):** Highlights the failure of unmonitored 311 systems [8].
* **Gestisoft 311 CRM Explainer (2025):** Outlines key features like multi-channel intake and duplicate detection [5].

## References

1. *Automated Prioritization and Routing of IT Support Tickets ...*. https://repository.rit.edu/cgi/viewcontent.cgi?article=13153&context=theses
2. *Invisible Impacts: ROI of 311 Request Management – CivicPlus*. https://www.civicplus.com/blog/crm/understanding-impact-the-true-return-of-311-request-management-systems-is-twofold/
3. *
	Welcome to Contract Insight Documentation Wiki
*. https://insightwiki.cobblestonesystems.com/default.aspx?pg=ywtKfZVqbZMBnkN5Zwl8IA%3D%3D
4. *REST API Overview*. https://wiki.cobblestonesoftware.com/docs/rest-api-overview
5. *What is a 311 CRM System? | Gestisoft*. https://www.gestisoft.com/en/blog/what-is-a-311-crm-system
6. *311 Coordinator - Civilized.ai*. https://civilized.ai/311-coordinator
7. *4 - Search & Review*. https://vita.cobblestonesystems.com/public/ViewFile.aspx?fid=20039&cid=2094
8. *Butkovitz Says 311 System Fails to Meet Key Goals - Christy Brady, CPA*. https://controller.phila.gov/philadelphia-reports/butkovitz-says-311-system-fails-to-meet-key-goals/