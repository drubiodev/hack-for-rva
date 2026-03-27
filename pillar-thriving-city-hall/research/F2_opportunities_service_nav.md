# Richmond 311 Navigation — Wizard-First, Search-Assisted, Risk-Managed

## Executive Summary
Richmond faces a critical service navigation challenge: routing residents accurately across ~50+ request types without a modern RVA311 API, relying instead on a Drupal-based rva.gov architecture. With RVA311 handling over 83,000 requests annually across 20+ partner agencies [1], the stakes for accurate routing are high. 

Recent municipal AI failures, notably NYC's $600,000 chatbot that was canceled in February 2026 for providing illegal advice [2] [3], demonstrate that open-ended LLM generation is too risky for public-facing government routing. Conversely, deterministic decision trees—like GOV.UK's "Smart Answers" [4] [5] —provide the necessary auditability and safety. 

The optimal solution for the hackathon prototype is a **"Wizard-First, Search-Assisted"** approach. This leverages a hard-coded, version-controlled decision tree to guide users who "don't know what they don't know," backed by a lightweight semantic search for users who know exactly what they need. This approach requires no live API, relies on a static taxonomy built from existing rva.gov content, and provides the safety, accuracy, and transparency that stakeholders like Pete Breil will require to greenlight the project post-hackathon.

## Context, Constraints, and Stakes
Richmond needs a low-risk, low-friction tool that routes accurately without live API dependencies. The operational scale is significant: RVA311 partners with over 20 different City agencies and processed over 83,000 requests in 2024 [1]. 

The technical constraints are strict. There is no post-2018 RVA311 API available, meaning the solution must operate independently of live ticketing systems. The city's web presence is Drupal-based (rva.gov), requiring a solution that can either be embedded as a component or linked externally. Furthermore, the taxonomy of ~50+ request types must be managed offline.

The political and risk landscape heavily favors deterministic safety over generative novelty. In New York City, the MyCity AI chatbot, which cost nearly $600,000 to build, was taken down by Mayor Zohran Mamdani in early 2026 after it was caught telling businesses to break the law [2] [3]. The Center for Democracy and Technology (CDT) explicitly warns that while LLMs can help agencies curate data and match intents, they "should not yet be used to respond to customers directly" due to hallucination risks and the high standard of care required for legal/government information [6].

## Comparative Analysis of Three Approaches

The following table evaluates the three proposed approaches against Richmond's specific constraints and risk profile.

| Dimension | Decision Tree (Wizard) | NLP/Semantic Search | LLM-Powered Chatbot |
|---|---|---|---|
| **Dataset needed** | ~50–70 category records with descriptions + 5–10 synonyms each; examples | Same as wizard + embeddings index; optional phrase logs | Full curated KB + prompt rules; fine-tuning/grounding; heavy governance |
| **Confidence handling** | Deterministic path; user confirms final selection | Confidence scores; top-3 suggestions; user confirms | Model certainty often miscalibrated; hallucination risk; hard to audit |
| **Fallbacks** | "I'm not sure" → show popular categories or call 3-1-1 | <0.80 confidence → top-3; <0.50 → 3-1-1 | Disclaimers; human escalation; still risky per NYC case |
| **Taxonomy w/o API** | Static JSON/YAML; versioned and auditable | Same static taxonomy; index synonyms/phrases | Same, plus retrieval grounding; higher complexity |
| **UX for unknown-unknowns** | Strong: guided, 3–6 steps reduce error (NN/G) [7] | Mixed: good for known terms; weaker for ambiguity | Conversational but untrusted for policy/legal topics [6] |
| **Build time (hackathon)** | Fast: 1–2 devs, 3–5 pages + JSON | Moderate: wizard + lightweight search index | Slow/risky: integration, guardrails, evals |
| **Risk profile** | Low; fully deterministic | Moderate; mitigated by thresholds and confirmation | High; public failures (NYC ~$600k) [2], reputational damage |
| **External evidence** | GOV.UK Smart Answers [4] [5] | San Diego audit warns about confusing outputs [8] | CDT: don't use LLMs for direct responses [6] |

**Key Takeaway:** A wizard-first approach with a semantic-search assist maximizes safety and coverage. LLM chat is entirely unacceptable for public answers given the recent NYC cancellation [2] [3] and CDT guidance [6]. Even established apps like San Diego's "Get It Done" (which processed over 390,000 reports [9]) faced a 2022 audit revealing that the app often gave "inaccurate, incomplete or confusing information," leading residents to still prefer calling the city 1 million times a year versus 300,000 app requests [8].

## Data and Taxonomy Plan
A complete offline taxonomy is feasible to build in 1–2 days by scraping and curating existing Drupal pages. Without API access, the minimum viable dataset is small, static, and highly structured.

**Sources for Curation:**
* The rva.gov "Browse By Service" directory [10].
* The Citizen Service & Response department pages and "Helpful Links" [11] [12].
* The public RVA311 portal (rva311.com) to observe actual request wording [1].

**Structure:**
Create a two-level taxonomy consisting of 8–12 super-categories branching down to 50–70 leaf request types. Each leaf node must contain:
* Title
* Description (1–2 sentences)
* 5–10 synonyms/lay terms
* 1–3 clarifying examples
* Routing URL (direct link to RVA311 or the specific rva.gov service page)
* Responsible department

**Governance:**
Store this taxonomy as a single JSON or YAML file. This allows the logic to be version-controlled in Git, making it fully auditable by the 311 team, mirroring the successful GOV.UK Smart Answers framework [4] [13].

## Confidence Calibration and Fallback Protocols
Uncertainty must be made visible. The tool should never auto-route a resident on low confidence, and it must escalate to human help early.

**Protocol:**
* **Wizard Flow:** Ends with a final confirmation screen featuring a "Why this?" explanation to build trust.
* **Search Flow:** 
 * If confidence is ≥0.80 (and ≥0.10 above the runner-up), preselect the category.
 * If confidence is 0.50–0.79, show the top 3 candidates with pros/cons.
 * If confidence is <0.50 or out-of-domain, immediately suggest calling the 311 Call Center at **3-1-1** or **804-646-7000** [1] [12].
* **Logging:** Store the query, suggested categories, confidence scores, and the user's final selection for audit purposes.

This conservative approach aligns with CDT's guidance that AI should assist in matching, not answering [6], and mitigates the risk of confusing users, as seen in the San Diego audit [8].

## UX for "Don't Know What They Don't Know"
For novices, a wizard reduces cognitive load and error. The Nielsen Norman Group (NN/G) explicitly recommends wizards for situations where users are unfamiliar with a process or lack domain expertise [7]. Conversely, search benefits repeat users who already know the exact municipal terminology (e.g., "missed trash pickup").

**Design Strategy:**
* **Lead with the Wizard:** Ask 3–6 plain-language questions to narrow intent. Show a clear progress indicator.
* **Provide Escape Hatches:** Include a prominent "Skip to search" button for confident users, and an "I'm not sure" branch that presents popular categories by theme.
* **Transparent Results:** The final page should show the top recommendation plus two alternates, complete with short explanations and direct routing links.

## Minimum Viable Feature Set for a Credible Demo
To prove viability in a 48-hour hackathon, the team must ship a wizard-first, search-assisted router with measurable accuracy and full auditability.

**MVP Features:**
* Static taxonomy JSON/YAML for ~50+ categories and synonyms.
* A 3–6 step mobile-first wizard.
* Lightweight semantic search over category titles, descriptions, and synonyms, displaying top-3 matches with confidence labels.
* Strict confidence thresholds with fallbacks to the 3-1-1 phone number (804-646-7000) [1].
* Direct routing links to RVA311.com or rva.gov service pages (no API required).
* An Admin/Audit view demonstrating routing logs, decisions, and change history.

**Success Metric for Demo:** Achieve ≥85–90% top-1 accuracy on a 30–50 query test set covering the top 20 categories, with zero critical misroutes.

## What Pete Breil and 311 Need to Greenlight Post-Hackathon
Accuracy, safety, maintainability, and a path to scale matter far more than technological novelty. To consider the prototype worth continuing, stakeholders will need to see:

* **Test Results:** A clear confusion matrix showing top-1 and top-3 accuracy, and proof that ambiguous cases are safely handed off to human agents.
* **Content Governance:** A clear workflow for who reviews and updates the static taxonomy, how often it happens, and how changes are audited.
* **Risk Controls:** Demonstrated thresholds, disclaimers, and clear handoffs to the 311 call center [1].
* **Operational Fit:** A plan for embedding the tool within the Drupal-based rva.gov environment without requiring heavy IT maintenance.

## Implementation Plan
A small team can ship this wizard+search hybrid with static data and governance in 48 hours.

* **Day 1:** Focus on taxonomy curation (2 people scraping rva.gov [14] and RVA311 [1]), UI scaffolding (1 dev), and building the lightweight search index (1 dev). Secure a content review from a 311 liaison.
* **Day 2:** Implement confidence logic and fallbacks, build the routing results pages, set up audit logging, run the acceptance test set, and finalize the demo script.
* **Tech Stack:** Static JSON/YAML; JS/TS front-end (designed as a potential Drupal component); simple embeddings (e.g., cosine similarity) or a robust keyword matcher. No external LLM should be called at runtime.

## Post-Hackathon Roadmap
Once the MVP is validated, the city can add data depth and automation incrementally, always with human oversight.

* Expand the taxonomy and add long-tail synonyms derived from actual call center logs (once that data becomes available).
* Use LLMs *offline* to mine synonyms and phrases, subject to human review before being added to the static JSON [6].
* Run A/B tests on the wizard flow and instrument drop-off analytics.
* Explore API reinstatement or CSV exports for providing live status updates in specific high-volume categories.

## Risks and Mitigations
* **Risk:** Misrouting users to the wrong department, causing frustration and delayed service.
 * **Mitigation:** Enforce conservative confidence thresholds and provide clear escalation paths to the 3-1-1 call center [1].
* **Risk:** Confusing language or biased synonyms.
 * **Mitigation:** Use plain-language rewrites, conduct community term vetting, and maintain a Git-based change control log for all taxonomy updates.
* **Risk:** Maintainability lapses if the taxonomy becomes outdated.
 * **Mitigation:** Establish quarterly audits and ensure the JSON/YAML structure is simple enough for non-developers to review.

## Evidence and References
The recommendations in this report align with proven government design patterns and documented municipal AI failures:
* **NYC MyCity Chatbot:** Failed due to hallucinated, illegal advice; cost ~$600k; canceled Feb 2026 [2] [3].
* **CDT Guidance:** Recommends using LLMs to curate data and match intents offline, but not to generate direct responses to the public [6].
* **GOV.UK Smart Answers:** Proven success using deterministic decision trees to hide policy complexity [4] [5].
* **San Diego Get It Done:** Despite >390,000 reports [9], an audit showed confusing app outputs led to 1,000,000 phone calls vs 300,000 app requests, highlighting the need for clear guidance and fallbacks [8].
* **Richmond Scale:** RVA311 handles 83,000 requests annually across 20+ agencies, accessible via 3-1-1 or 804-646-7000 [1] [12].

## References

1. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
2. *Mamdani to kill the NYC AI chatbot we caught telling businesses to break the law – The Markup*. https://themarkup.org/artificial-intelligence/2026/01/30/mamdani-to-kill-the-nyc-ai-chatbot-we-caught-telling-businesses-to-break-the-law
3. *Impact: Chatbot Canceled | THE CITY - NYC News*. https://www.thecity.nyc/impact-chatbot-cancelled/
4. *Smart answer - GOV.UK Publishing Design Guide*. https://design-guide.publishing.service.gov.uk/frontend-templates/smart-answer/
5. *Smart answers are smart – Government Digital Service*. https://gds.blog.gov.uk/2012/02/16/smart-answers-are-smart/
6. *Let LLMs Do the Talking? Generative AI Issues in Government Chatbots - Center for Democracy and Technology*. https://cdt.org/insights/let-llms-do-the-talking-generative-ai-issues-in-government-chatbots/
7. *Wizards: Definition and Design Recommendations - NN/G*. https://www.nngroup.com/articles/wizards/
8. *New audit says San Diego’s Get It Done app often gives inaccurate, incomplete or confusing information – San Diego Union-Tribune*. https://www.sandiegouniontribune.com/2022/10/07/new-audit-says-san-diegos-get-it-done-app-often-gives-inaccurate-incomplete-or-confusing-information-3/
9. *San Diego, CA expanded their 311 "Get It Done" app for better customer engagement - Govlaunch Projects*. https://govlaunch.com/projects/san-diego-ca-expanded-their-311-get-it-done-app-for-better-customer-engagement
10. *| Richmond*. https://www.rva.gov/
11. *RVA 311 Helpful Links | Richmond*. https://www.rva.gov/citizen-service-and-response/rva-311-helpful-links
12. *Citizen Service and Response | Richmond*. https://www.rva.gov/citizen-service-and-response
13. *Application: smart-answers - GOV.UK Developer Documentation*. https://docs.publishing.service.gov.uk/repos/smart-answers.html
14. *Services | Richmond*. https://rva.gov/common/services