# Right Tech, Right Place: A practical boundary map for city service automation

## Executive Summary

City governments face immense pressure to modernize services using artificial intelligence and automation. However, recent municipal deployments reveal a stark divide between where software genuinely improves operations and where it causes active harm. This report establishes a practical boundary map for city service automation, focusing on service navigation (311) and procurement. 

The data reveals that software excels at information retrieval, pattern recognition, and decision support, but fails dangerously when tasked with unsupervised legal determinations or complex human judgments. For example, while data-driven "red flag" analytics in procurement have successfully recovered millions of dollars and increased supplier diversity globally [1], generative AI chatbots deployed for public service navigation have provided illegal advice and eroded public trust, leading to costly shutdowns [2] [3]. To safely harness automation, cities must implement strict "human-in-the-loop" policies, constrain public-facing AI to cite-and-link retrieval, and reserve high-stakes decisions for trained civil servants [4] [5].

## Purpose and Scope

This report pinpoints where software reliably helps city service delivery and procurement—and where human judgment must remain in charge. By mapping these boundaries, civic technologists and government IT leaders can deploy technology that saves time and reduces cognitive load without risking legal liability, equity, or public trust. The scope covers specific do/don't maps for 311 service navigation and procurement, backed by recent municipal AI policies and real-world case studies.

## What Software Can Do vs. Where It Fails in City Hall

Software interventions in city government succeed when they are scoped to retrieval, patterning, and decision support. They fail when they attempt to replace human judgment in high-stakes, ambiguous, or legally binding contexts.

**Where Software Helps:**
* **Information Retrieval:** Surfacing plain-language answers from vetted, static content [6].
* **Pattern Recognition:** Identifying anomalies in structured data, such as contract expiry dates or unusual bidding behaviors [7].
* **Decision Support:** Automating routine "read-work" to reduce cognitive load, allowing humans to focus on complex evaluations [8].

**Where Software Fails or Causes Harm:**
* **Actionable Decisions:** San José's AI guidelines explicitly state that staff must not let AI make actionable decisions, such as responding to emergencies or approving applications [9].
* **Fully Automated Material-Impact Decisions:** Louisville and Seattle policies prohibit fully automated decisions that create a material impact on individuals without meaningful human oversight [4] [5].
* **Unsupervised Legal/Financial Guidance:** Generative AI systems lack the nuanced judgment and ethical reasoning required to interpret complex legal or financial situations [10].

## Field Evidence: Successes and Cautionary Failures

Real-world deployments demonstrate the stark contrast between well-scoped analytics and unbounded generative AI.

### Success: Procurement Red Flags Analytics
When used as an alerting mechanism for human investigators, data analytics deliver outsized integrity gains. The Open Contracting Partnership (OCP) methodology for calculating risk indicators has proven highly effective [1]:
* **Dominican Republic:** The procurement agency monitors processes in real time using 21 targeted red flags. In 2023, this resulted in more than 60 suppliers being debarred. Open procedures increased from 94% (2020) to 96% (2023), single-bid tenders decreased from 63% to 60%, and supplier diversity increased by 27% with over 20,000 new suppliers registered [1].
* **Kazakhstan:** The redflags.ai platform helped financial police open 120 criminal cases in 2010, recovering $77 million. In 2021, it helped prosecutors cancel 505 illegal tenders worth $331 million, and the government reported $86 million in savings [1].
* **Italy:** The Anticorruption Agency (ANAC) launched a tool applying more than 70 indicators to automate the detection of corruption risks [1].

### Failure: NYC MyCity Chatbot
Conversely, deploying generative AI for public-facing advice without strict guardrails leads to severe liabilities. New York City launched the MyCity chatbot in October 2023 to help business owners navigate regulations [2]. 
* **Harmful Outputs:** The bot confidently told businesses to break the law, advising that employers could take a cut of workers' tips, that landlords could discriminate against Section 8 vouchers, and that businesses could refuse cash payments [2] [11] [12].
* **Ineffective Disclaimers:** Despite adding disclaimers that the bot was a "beta product" and should not be used for legal advice, the system continued to provide false information [11] [12].
* **Costly Shutdown:** The bot, which reportedly cost nearly $600,000 to build, was ultimately shut down in February 2026 by the new mayoral administration, which deemed it "functionally unusable" [3].

## Service Navigation Boundary: Software vs. 311 Agent

For 311 and service navigation, software should automate findability and form-filling support, while escalating anything involving high stakes, ambiguity, or emotional distress to a human agent. Canada's guidance for AI help applications emphasizes that tools should assist users by retrieving answers from already published official information, ensuring consistency and transparency [6].

| Resident Intent / Situation | Software Do (Appropriate Role) | Software Don't (Boundary) | Escalation Trigger |
| :--- | :--- | :--- | :--- |
| **"What hours is X open?" / "Where to apply for Y?"** | Retrieve and display answers directly from official pages with citations [6]. | Invent answers or summarize beyond the source text. | None, if answerable with a direct link. |
| **"Is my landlord allowed to...?"** | Surface relevant policy pages; warn that legal advice requires an agent. | Provide normative or interpretive legal advice [2]. | Legal/financial impact keywords (eviction, fines, withholding rent). |
| **Report pothole / graffiti / trash** | Guided triage; auto-fill location data; attach photos; confirm SLA. | Decide priority where multi-factor community tradeoffs exist. | Safety/health risks, repeat reports. |
| **Benefit eligibility pre-check** | Calculator using published criteria; list required documents. | Make final eligibility or appeal determinations. | Edge-case rules, missing documents. |
| **Mental health / safety / welfare** | Provide hotline info; execute warm transfer to human. | Engage in counseling or discretionary risk routing. | Keywords indicating harm, abuse, or crisis. |

*Key Takeaway:* Constrain resident-facing assistants to cite-and-link answers from vetted pages. Block free-form "advice" and ensure prominent "Talk to a person now" controls are available.

## Procurement Boundary: Software vs. Procurement Officer

In public procurement, software is highly effective at extraction, patterning, and anomaly detection, but weak at qualitative judgment. The National Institute of Governmental Purchasing (NIGP) notes that while AI can streamline spend analysis and flag risks, critical thinking and human judgment are essential to evaluate findings and make balanced decisions [7] [10].

| Task | Software Do (Appropriate Role) | Software Don't (Boundary) | Human Owner |
| :--- | :--- | :--- | :--- |
| **Contract metadata extraction** | Auto-extract terms, dates, renewal/expiry; flag change-order spikes [7]. | Amend terms or trigger auto-renewals autonomously. | Contract Manager |
| **Spend analysis & Fraud detection** | Categorize spend; detect anomalies, unusual bidding behavior, or invoice discrepancies [7]. | Declare fraud or autonomously sanction suppliers. | Procurement Analytics Lead |
| **Red flags risk scoring** | Apply indicator libraries (e.g., OCP's 73 indicators) and send alerts [1]. | Auto-disqualify bids or auto-award contracts. | Integrity Unit |
| **Supplier screening** | Aggregate public data, certifications, and debarment lists [7]. | Make final "responsibility" or "responsiveness" findings. | Procurement Officer |
| **Proposal review support** | Highlight clause gaps; summarize sections based on natural language processing [8]. | Assign final scores or rank offers [8]. | Evaluation Committee |

*Key Takeaway:* Automate the "read-work" (clause extraction, expiry alerts) and reserve the "think-work" (evaluations, responsibility findings, award decisions) for trained procurement officers.

## Governance Guardrails to Stay in the "Appropriate Software Role"

To ensure software remains in its appropriate role, cities must implement robust governance frameworks centered on human oversight and transparency.

* **Meaningful Human Oversight:** Louisville's AI policy mandates "Meaningful Human Oversight," defined as timely and effective human involvement by trained personnel with the authority to override, correct, or halt the AI system's use [4].
* **Prohibited Uses:** Policies in Seattle and Louisville explicitly prohibit fully automated decisions that create a material impact on individuals without an accessible path for human review [4] [5].
* **Transparency and Notice:** When residents interact with an AI system, cities must provide clear notice that AI is being used and offer a method to reach a human for assistance [4].
* **Auditability:** Systems must maintain audit trails. Louisville requires retaining logs and maintaining an internal AI System Inventory of approved use cases and risk classifications [4].

## Data Readiness and Standards

Great technology relies on high-quality data. The Open Contracting Partnership emphasizes that data standardization, interoperability, and portability are critical for effective procurement analytics [13]. 
* **Standardization:** Implementing the Open Contracting Data Standard (OCDS) allows governments to easily map the 73 common risk indicators to their procurement data [1].
* **Preparation:** Governments should conduct data-readiness sprints to clean data and build capability using small, low-risk pilots before rolling out larger analytical tools [14].

## Implementation Roadmap and KPIs

Cities should adopt a bounded, iterative approach to automation:
1. **Start Narrow:** Begin with low-risk, reversible use-cases (e.g., contract date alerts, internal knowledge retrieval) [14].
2. **Establish Success Gates:** Define strict accuracy and safety thresholds before public launch. For example, require a 95% exact-match accuracy rate to source content during offline testing.
3. **Monitor KPIs:** Track human escalation rates on high-stakes intents, average time-to-human, complaint rates, and the number of investigated red flags leading to actionable integrity outcomes.

## Hackathon Demo Script: Explain Limits Without Killing Excitement

When demonstrating civic tech prototypes, use plain language to explain boundaries while highlighting user benefits:

> "This assistant is designed to save you time by instantly retrieving answers from official city pages, and it always shows its sources. However, it is not a lawyer. If your question involves legal, financial, or safety consequences, the system will immediately offer a fast handoff to a trained human agent. 
> 
> On the procurement side, our dashboard acts as a radar—it flags unusual patterns like change-order spikes or clustered bids. But the software doesn't make the call; it surfaces the data so our procurement officers can make informed, accountable decisions. Every flag has an audit trail. This is assisted digital—less time searching, more time helping."

## Risk Register and Mitigations

* **Wrongful Legal/Policy Advice:** Mitigate by scoping public chatbots strictly to retrieval from versioned content, blocking generative advice, and requiring human handoffs for high-stakes keywords [6] [2].
* **Scope Creep:** "Helpful" tools can drift into harmful surveillance (e.g., pothole cameras used for tracking) [14]. Mitigate by locking use-case boundaries in policy and requiring AI Impact Assessments for any repurposing [4].
* **Automation Bias:** Humans may blindly trust AI outputs. Mitigate by requiring critical thinking training for staff and ensuring AI outputs are treated as recommendations requiring human validation [10].

## Appendices

* **Indicator Libraries:** Refer to the Open Contracting Partnership's guide detailing 73 common red flag indicators mapped to the OCDS [1].
* **Policy References:** 
 * Louisville AI Policy (Definitions of Meaningful Human Oversight, Prohibited Uses) [4].
 * Seattle AI Policy (Prohibition of fully automated high-impact decisions) [5].
 * San José AI Guidelines (Prohibition on actionable decisions) [9].
 * Canada.ca Guidance for AI help applications [6].

## References

1. *Red flags in public procurement*. https://www.open-contracting.org/wp-content/uploads/2024/12/OCP2024-RedFlagProcurement-1.pdf
2. *NYC’s AI Chatbot Tells Businesses to Break the Law – The Markup*. https://themarkup.org/artificial-intelligence/2024/03/29/nycs-ai-chatbot-tells-businesses-to-break-the-law
3. *Mamdani to kill the NYC AI chatbot we caught telling businesses to break the law – The Markup*. https://themarkup.org/artificial-intelligence/2026/01/30/mamdani-to-kill-the-nyc-ai-chatbot-we-caught-telling-businesses-to-break-the-law
4. *Artificial Intelligence (AI) Policy | LouisvilleKY. ...*. https://louisvilleky.gov/government/metro-technology-services/artificial-intelligence-ai-policy
5. *Artificial Intelligence (AI) Policy*. https://seattle.gov/documents/departments/tech/privacy/ai/artificial_intelligence_policy-pol211%20-%20signed.pdf
6. *Guidance for the design of AI help applications on Canada.ca - Canada.ca*. https://design.canada.ca/guidance/ai/index.html
7. *Artificial Intelligence: The Impact on Public Procurement - Opportunity & Risk*. https://www.nigp.org/blog/ai-and-public-procurement
8. *When Artificial Intelligence Buys for Us — Transparency and Accountability in AI-Driven Procurement*. https://www.nigp.org/blog/when-ai-buys-for-us
9. *
	
    San José AI Guidelines and Policies | City of San José

*. https://www.sanjoseca.gov/your-government/departments-offices/information-technology/itd-generative-ai-guideline
10. *Embracing the AI Era: Why Upskilling in Critical Thinking is Essential *. https://www.nigp.org/blog/embracing-ai-era
11. *New York City defends AI chatbot that advised entrepreneurs to break laws | Reuters*. https://www.reuters.com/technology/new-york-city-defends-ai-chatbot-that-advised-entrepreneurs-break-laws-2024-04-04/
12. *Malfunctioning NYC AI Chatbot Still Active Despite Widespread Evidence It’s Encouraging Illegal Behavior | THE CITY — NYC News*. https://www.thecity.nyc/2024/04/02/malfunctioning-nyc-ai-chatbot-still-active-false-information/
13. *New UN procurement guidelines support governments to adopt the right technology for the fight against corruption - Open Contracting Partnership*. https://www.open-contracting.org/2025/12/12/new-un-procurement-guidelines-support-governments-to-adopt-the-right-technology-for-the-fight-against-corruption/
14. *AI for Government: How Public Procurement Can Adopt It Without Getting Burned - NASPO*. https://www.naspo.org/news/ai-for-government-how-public-procurement-can-adopt-it-without-getting-burned/