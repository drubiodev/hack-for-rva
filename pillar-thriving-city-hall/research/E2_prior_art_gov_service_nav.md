# From 311 to AI Navigators: What Actually Works in Government Service Discovery

## Executive Summary

- **Integrated, plain-language intakes unlock real outcomes:** Code for America’s GetCalFresh helped 6.2 million people secure $12.8 billion in food assistance between 2017 and 2025, driving over 70% of online SNAP applications in the state and lifting California’s SNAP participation rate from 66% in 2014 to 81% in 2022 [1]. Prioritize a single, mobile-first intake with human-centered copy over department-centric pages for Richmond’s prototype.
- **Time saved is equity gained:** The MNbenefits project cut application time from approximately an hour to about 12 minutes, successfully submitting over 12,000 applications for more than 25,000 people by mid-2021 [2]. Ruthlessly reduce steps and questions; set a target of under 10 minutes to route residents to the right Richmond service.
- **Open-ended LLM legal/compliance advice is a liability, not a feature:** NYC’s Microsoft-powered business chatbot confidently recommended illegal actions (e.g., source-of-income discrimination, taking workers’ tips), prompting months of criticism and its eventual takedown in February 2026 [3] [4]. Prohibit generative "advice" and constrain answers to verbatim, cited government sources.
- **Bounded AI with curated sources scales safely and fast:** The City of Austin stood up an IBM watsonx Assistant in just one week for COVID-19 information, pre-loaded with CDC and local guidance [5]. Similarly, Citibot’s Lex+Kendra pattern added a search fallback when intents fail, reportedly saving Opelika, AL 2,500 hours of resident wait time over three years [6] [7]. 
- **Multichannel human support sustains outcomes at scale:** GetCalFresh layered live chat, SMS updates, and document uploads [1] [8]. Pair the navigator with SMS follow-ups and real-time chat escalation to prevent drop-off.
- **Transparency beats disclaimers:** NYC’s bot added stronger disclaimers but still returned inaccurate guidance [9]. In contrast, Ask Indiana includes terms and conditions but also links directly to state webpages for more information [10]. Require answer-level citations and "view source" links; if the system cannot cite, it should not answer.

## Purpose and Scope

The goal of this research is to synthesize national lessons from integrated benefits platforms, city chatbots, and federal virtual assistants to inform a safe, effective government service navigator prototype for Richmond. By examining both highly successful human-centered design projects and cautionary tales of unbounded AI deployments, we can architect a solution that connects residents to the right services without exposing the city to legal liability or eroding public trust.

## Landscape Inventory

Successful tools tightly couple plain-language design with bounded automation. Failures stem from unconstrained Large Language Models (LLMs) giving legal or compliance advice.

### Prior Art Comparison

| Tool/Owner | Problem & Users | Technical Approach | Primary Data Sources | Documented Outcomes | Notable Design Decisions | Risks/Cautions |
|---|---|---|---|---|---|---|
| **GetCalFresh** (Code for America) | SNAP applicants facing long, repetitive online flows | Guided digital assister; streamlined intake; SMS; live chat | County/state SNAP systems; client feedback | 6.2M people, $12.8B benefits (2017–2025); 70%+ of online SNAP apps; participation rose 66%→81% [1] | Plain language; mobile-first; doc upload; human chat [1] [8] | Requires tight government partnership |
| **MNbenefits** (MN + CfA) | Multi-benefit applications too long and siloed | Integrated intake across 9 benefits; HCD | State benefits systems | <12 min to complete vs ~60 min; >12k apps for >25k people by mid-2021 [2] | "Less than 20 min" north star; progressive disclosure [2] | Ongoing maintenance across programs |
| **BenefitsCal** (CA) | Statewide unified portal | State-run portal informed by CfA patterns | County/state systems | Scaled principles statewide (2021–2023) [1] | Embedded plain language, uploads, multilingual [1] | Large program governance needed |
| **Citibot Deployments** (Multiple Cities) | High call volume; need 24/7 answers | NLUs via Amazon Lex + enterprise search via Kendra fallback [7] | Curated city/state/federal pages; CSV FAQs [7] | 94% inbound handled; 2,500 hours saved (Opelika); NOLA 76% Qs via text; Arlington +523% engagement [6] [11] | Search fallback when intents fail; SMS and web; 75+ languages [6] [7] [11] | Content drift if not curated |
| **Austin COVID Virtual Assistant** (IBM) | Surge of COVID inquiries | Watson Assistant; fast-deploy template [5] | CDC + local/state guidance [5] | Deployed in 1 week; understands dozens of topics [5] | Pre-loaded intents; free 90-day launch [5] [12] | Narrow domain; must update frequently |
| **USCIS "Emma"** (Federal) | High-volume immigration FAQs | Early virtual assistant (NLP) [13] [14] | USCIS content | 24,835 pageviews in first month (Dec 2015) after promo [14] | Prominent A–Z index + assistant [14] | Lack of public accuracy metrics |
| **Ask Indiana** (State) | General state services Q&A | Generative AI chatbot (Tyler Technologies) [10] | IN.gov pages [10] | Launched May 2025; handles BMV hours, refuses sensitive topics [10] | Terms disclose inaccuracy; links to sources [10] | Gen-AI risk envelope |
| **NYC Business AI Chatbot** (City) | Business owners navigating complex rules | LLM-based assistant over 2,000+ pages [3] | NYC Business content; MS AI [3] [9] | Reported illegal/inaccurate advice; taken down Feb 2026 [3] [4] | Added disclaimers post-criticism; inconsistent answers [9] | Strong caution: avoid unbounded generative "advice" |

**Key Takeaways:** The most impactful tools (GetCalFresh, MNbenefits) focus on reducing friction and time-to-completion through human-centered design. AI chatbots can provide rapid value when strictly bounded to curated sources (Austin, Citibot), but pose severe reputational and legal risks when allowed to generate unverified compliance advice (NYC).

## Technical Approaches

Favor bounded retrieval and deterministic flows. Use LLMs for routing and summarization, not statutory advice.

### Decision Trees and "Smart Answers" for High-Stakes Routing
- **Example:** MNbenefits integrated intake across nine programs; GetCalFresh guided flows [1] [2].
- **Use for:** Eligibility screening, required documents, appointment scheduling.
- **Guardrails:** Explicit logic, auditability, and progressive disclosure.

### Enterprise Search + Retrieval QA (RAG) for FAQs
- **Example:** Citibot’s Amazon Lex + Kendra fallback architecture; Austin’s CDC-grounded Watson assistant [7] [5].
- **Use for:** Hours, locations, and "how do I…" queries with stable, citable pages.
- **Guardrails:** Source whitelists, per-answer citations, and confidence thresholds.

### Classic NLP Virtual Assistants for Known Intents
- **Example:** USCIS Emma; pre-authored intents plus search fallback [13] [14].
- **Use for:** Top 100 intents with high volume and low policy risk.

### Generative Chat for Low-Risk Tasks Only
- **Cautionary:** The NYC bot hallucinated compliance guidance, telling landlords they could discriminate based on housing vouchers and telling businesses they could take workers' tips [3].
- **Use for:** Paraphrasing, multi-lingual rewording, and summarizing linked sources—never as a source of truth.

## Design Patterns That Work

Outcomes come from content design and operations, not just technology.

- **Plain-language, resident vocabulary:** GetCalFresh refined the language used in applications to better reflect how clients actually think about their household and income situations [1]. 
- **Human fallback and SMS:** Live chat support teams and text message reminders are critical. Louisiana scaled text messages to over 400,000 people to help them stay enrolled during COVID-19 [15] [1].
- **Mobile-first, document uploads:** Allowing applicants to upload necessary paperwork using mobile phone cameras slashed application times [8].
- **Analytics loop with a north-star:** MNbenefits set a clear target to prove an integrated application could be submitted in less than 20 minutes, ultimately achieving a 12-minute average [2]. 
- **Multilingual at launch:** Code for America scaled multiple languages as products grew, and vendors like Citibot support 75+ languages out of the box [1] [6].
- **"No link, no answer":** Source transparency builds trust. Ask Indiana provides links to state webpages alongside its chat responses [10].

## Patterns to Avoid

Do not let an LLM invent policy, and do not rely on disclaimers to save trust.

- **Unbounded legal/compliance advice:** NYC's chatbot provided dangerously inaccurate information on housing policy and worker rights. Despite widespread criticism, the city initially kept it online before Mayor Mamdani finally killed the project in February 2026 [3] [16] [4].
- **Disclaimers as a crutch:** NYC updated its chatbot page to explicitly tell users "Do not use its responses as legal or professional advice," yet the bot itself would still tell users it *could* be used for professional business advice [9]. 
- **Content drift:** Without curation, search indices and models go stale. Information must be routinely indexed for updated information, as seen in Citibot's DynamoDB table approach for frequently changing COVID data [7].

### Patterns to Emulate vs. Avoid

| Do this | Avoid this | Why |
|---|---|---|
| Retrieval-only answers with citations | Freeform LLM advice on regulations | Trust and defensibility |
| Single "Start here" intake, plain language | Department-first navigation | Conversion and equity |
| Human fallback + SMS reminders | Bot-only support | Reduce churn, increase completion |
| KPIs on answerability, escalation, time | Vanity metrics (visits only) | Optimize for resident outcomes |
| Curated, whitelisted sources | Open web or uncited blobs | Accuracy and governance |

**Key Takeaways:** Disclaimers do not absolve a city of the harm caused by bad advice. Systems must be designed to refuse to answer if they cannot pull from a verified, cited source.

## Richmond Prototype Architecture

Build a bounded navigator: decision-tree triage + retrieval QA over a curated corpus, with human fallback and mandatory citations.

### Minimum Viable Stack (48–72 hours)
- **Frontend:** Lightweight web widget + SMS entry point.
- **Triage:** Deterministic decision tree to classify into top 20 intents (benefits, housing, permits, payments, IDs).
- **Knowledge base:** Curated corpus (RVA.gov, Virginia state services, Benefits.gov program pages, local CBOs), stored as chunked JSON + embeddings; nightly refresh.
- **Retrieval QA:** RAG that only surfaces verbatim excerpts and linked sources; if confidence is below a threshold or there is no source, refuse and escalate.
- **Languages:** English/Spanish with glossary-driven translations.
- **Fallback:** Live chat queue and "request a callback" form.
- **Telemetry:** Log queries, sources cited, time-to-answer, and "couldn’t answer" topics.

### Guardrails
- **Compliance mode:** No legal or eligibility determinations; provide citations and direct to official applications.
- **"No-citation, no-answer":** Strict enforcement.
- **Sensitive topics refusal list:** Safe redirections (e.g., legal aid, crisis hotlines), similar to Ask Indiana's refusal to answer sensitive HR questions [10].

### Suggested Components (Cloud-Agnostic Options)
- **Search:** OpenSearch, Azure Cognitive Search, or Amazon Kendra (which natively handles.pdf,.csv, and.html files) [7].
- **Orchestration:** Lightweight serverless functions (e.g., AWS Lambda) [7]; guardrails library.
- **SMS:** Twilio [7].
- **Content ops:** Simple CMS or Git-backed repo with YAML/Q&A pairs.

## Content and Taxonomy Plan

A modular taxonomy and Q&A library enables reuse across city departments and channels.

- **Start set:** Top 100 resident intents (pulled from 311 logs and web analytics).
- **Structure:** Each Q&A includes title, variants, source URLs, excerpt, last-reviewed date, language variants, and owner.
- **Workflow:** Department stewards review quarterly; change alerts trigger on source updates.

## Safety, Transparency, and Governance

Transparency per answer and clear accountability are non-negotiable.

- **Answer UI:** Prominent "Source: [Agency]" with link; "This is not legal advice."
- **Audit:** Store prompt, retrieved docs, answer, and operator actions.
- **Oversight:** Weekly review of low-confidence and escalated topics; publish a public changelog.

## Metrics and Trial Plan

Success equals faster, accurate, equitable help with fewer handoffs.

- **Core KPIs:** 
 - Answerability coverage (% queries with cited answer)
 - Time-to-cited-answer (p50/p90)
 - Escalation rate to human
 - "Couldn’t answer" topic backlog burn-down
 - CSAT by language
 - Equity: usage and success rates by channel and language
- **Targets (Phase 1):** 70%+ answerability with citations; p50 ≤ 20s; escalations 15–25% (healthy); CSAT ≥ 4.3/5.

## Implementation Roadmap

Ship a safe v1 in days; harden and expand within a month.

- **Week 0–1 (Hackathon):** Curate top 100 intents; build RAG + decision-tree triage; English/Spanish; live chat fallback; dashboards.
- **Week 2:** Add SMS; expand corpus; run red-team tests (policy/legal traps).
- **Week 3:** Department steward onboarding; publish public model card and governance page.
- **Week 4:** Pilot with 2–3 departments; collect metrics; plan iteration.

## Risks and Mitigations

Tight scoping, citations, and human fallback neutralize the biggest risks.

- **Hallucinations:** Mitigate via retrieval-only answers; enforce refusal + escalation.
- **Content drift:** Mitigate via nightly recrawls, steward reviews, and freshness flags.
- **Legal exposure:** Mitigate by providing no advice; always link to authoritative sources; disclaimers supplement, but do not substitute, accuracy.
- **Accessibility/language gaps:** Mitigate via screen-reader tested UI, bilingual launch, and phased language expansion.
- **Adoption:** Mitigate by promoting a "Start here" portal on the homepage, utilizing SMS shortcodes, and partnering with community organizations.

## References

1. *Simplifying California's Online Application for Food Benefits — Code for America*. https://codeforamerica.org/success-stories/simplifying-californias-online-application-for-food-benefits/
2. *Four Lessons from Our Journey to Deliver Human-Centered Integrated Benefits — Code for America*. https://codeforamerica.org/news/four-lessons-from-our-journey-to-deliver-human-centered-integrated-benefits/
3. *NYC’s AI Chatbot Tells Businesses to Break the Law – The Markup*. https://themarkup.org/artificial-intelligence/2024/03/29/nycs-ai-chatbot-tells-businesses-to-break-the-law
4. *Mamdani to kill the NYC AI chatbot we caught telling businesses to break the law – The Markup*. https://themarkup.org/artificial-intelligence/2026/01/30/mamdani-to-kill-the-nyc-ai-chatbot-we-caught-telling-businesses-to-break-the-law
5. *City of Austin | IBM*. https://www.ibm.com/case-studies/city-of-austin-watson
6. *Web Chat Solution — Citibot*. https://www.citibot.io/web-chat
7. *How Citibot’s chatbot search engine uses AI to find more answers | Artificial Intelligence*. https://aws.amazon.com/blogs/machine-learning/how-citibots-chatbot-search-engine-uses-ai-to-find-more-answers/
8. *California Launches Code for America’s GetCalFresh in all 58 Counties — Code for America*. https://codeforamerica.org/news/california-launches-code-for-americas-getcalfresh-in-all-58-counties/
9. *Malfunctioning NYC AI Chatbot Still Active Despite Widespread Evidence It’s Encouraging Illegal Behavior | THE CITY — NYC News*. https://www.thecity.nyc/2024/04/02/malfunctioning-nyc-ai-chatbot-still-active-false-information/
10. *Meet 'Ask Indiana,' state government's new AI chatbot • Indiana Capital Chronicle*. https://indianacapitalchronicle.com/2025/05/15/meet-ask-indiana-state-governments-new-ai-resident-assistant-chatbot/
11. *Text Chat Solution — Citibot*. https://www.citibot.io/text-chat
12. *IBM's Watson to Help Austin Residents Navigate COVID-19*. https://www.govtech.com/products/IBMs-Watson-to-Help-Austin-Residents-Navigate-COVID-19.html
13. *Emma, USCIS' New Virtual Assistant, Can Soon Answer Your Visa Questions - Nextgov/FCW*. https://www.nextgov.com/emerging-tech/2015/11/emma-uscis-new-virtual-assistant-can-soon-answer-your-visa-questions/124015/
14. *Online Communications Insights and Statistics – December ...*. https://www.uscis.gov/sites/default/files/document/reports/uscis-govMonthlyStatsReport-2015-12.pdf
15. *Integrated benefits applications — Code for America*. https://codeforamerica.org/programs/social-safety-net/integrated-benefits/
16. *NYC's AI chatbot was caught telling businesses to break the law. The city isn't taking it down | AP News*. https://apnews.com/article/new-york-city-chatbot-misinformation-6ebc71db5b770b9969c906a7ee4fae21