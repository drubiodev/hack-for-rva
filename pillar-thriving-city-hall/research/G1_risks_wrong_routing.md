# Stopping Confidently Wrong 311 Routing in Richmond: Guardrails for High-Stakes Service Navigation

## Executive Summary
Misrouting municipal service requests is not a rare edge case; it is a systemic failure that degrades trust and, in urgent scenarios, threatens public safety. Before centralizing its 311 system, Minneapolis found that 20 to 30 percent of calls were misrouted, including more than 60 percent of calls to police [1]. When AI and automated routing tools are introduced, the risk of "confidently wrong" routing amplifies. New York City's recent AI chatbot deployment serves as a stark warning: the bot confidently dispensed illegal business advice, and simply adding disclaimers failed to mitigate the harm, ultimately leading to the tool's shutdown [2] [3]. 

For Richmond, overlapping departmental responsibilities—such as the Department of Public Works (DPW) handling potholes and the Department of Public Utilities (DPU) managing water mains—create predictable routing seams where automated guesses can delay critical interventions [4] [5]. To safely deploy a 311 service navigation tool, Richmond must prioritize abstention over assertion. This requires strict confidence thresholds, mandatory source citations, and immediate escalation pathways for emergencies, ensuring the tool defaults to "I don't know—please call 311" rather than making a dangerous low-confidence guess.

## Context and risk framing — Wrong routing is a frequent, high-cost failure with outsized harm in urgent cases
Wrong routing is a frequent, high-cost failure with outsized harm in urgent cases. Historical data from municipal systems demonstrates the scale of the problem: prior to establishing its 311 system, Minneapolis reported that 20 to 30 percent of calls were misrouted, with police misdirects exceeding 60 percent [1]. 

When misrouting intersects with health and safety, the consequences are severe. The FCC notes that approximately 12% of wireless 911 calls arrive at the incorrect Public Safety Answering Point (PSAP) [6]. Transferring these misrouted calls introduces an estimated delay of a minute or more, consuming over 200,000 hours per year of excess 911 professional labor and contributing to confusion that can have deadly consequences [6]. 

Furthermore, deploying AI without strict guardrails invites harm. New York City's MyCity chatbot, launched to help small businesses, was caught dispensing bizarre advice that misstated local policies and advised companies to violate the law [2]. The bot falsely suggested it was legal to fire a worker who complains about sexual harassment or to serve cheese nibbled on by a rodent [2]. This highlights the severe risks of overconfident classification in civic tech.

## Downstream consequences of wrong routing — From minutes to days, with trust and safety impacts
When a resident submits a request to the wrong department, the request often enters a "blackhole." Legacy processes and siloed departments create gaps where resident requests vanish from view, leading to duplicate reports, misrouted tasks, and constant phone calls asking for status updates [7]. 

### Specific wrong-routing scenarios in Richmond with consequences
Richmond's specific infrastructure and departmental boundaries create high-risk routing seams. For example, DPW fills approximately 22,000 potholes annually [5], while DPU manages the city's water treatment and over 1,000 miles of water lines [4]. 

| Scenario | Likely Confusion | Wrong Route Consequence | Harm Risk |
| :--- | :--- | :--- | :--- |
| Street hole with active water flow | DPW pothole vs. DPU water main/leak | Days lost if sent to DPW queue while a leak persists. | High: roadway failure, water supply risk. A May 2025 sinkhole and water main break threatened the regional water supply [8]. |
| Graffiti on private property | DPW graffiti (public) vs. code enforcement (private) | Back-and-forth reassignment; property left defaced; complainant fatigue. | Medium: blight, business impacts. DPW handles public graffiti [5]. |
| Illegal dumping vs. bulky pickup | Solid waste vs. code enforcement | No pickup if routed to bulk; repeat dumping. | Medium: sanitation, pests. DPW handles Bulk and Brush [5]. |

*Takeaway: Richmond's DPW/DPU boundaries create predictable seam risks. Design must anticipate these overlaps and support dual-routing or human triage rather than forcing a single automated guess.*

### Manual rerouting latency and resident experience
While exact manual rerouting times are rarely published, operational cues indicate that delays compound across queues, especially during off-hours. Before its 311 implementation, Minneapolis received over 22,000 after-hours calls per year to its general number, leaving citizens without assistance when no one was available [1]. When requests are misrouted, staff must manually reassign them, creating extra work and unnecessary waiting [9]. Residents experience this as a lack of transparency, often requiring them to call 311 directly to check the status of a service request [10].

## Confidence calibration and overconfidence risk — Design for abstention, not assertion
Overconfident AI in civic contexts has already produced harmful guidance. The NYC MyCity chatbot repeatedly gave illegal advice, such as telling employers they could take a cut of their workers' tips [11] [12]. Even after the city updated the site to prominently describe the bot as a "beta product" and warned users not to use its responses as legal advice, the bot continued to provide false information [13]. 

Generative AI platforms are known to sometimes make things up or assert falsehoods with high confidence [11]. Because of this, relying solely on disclaimers is insufficient. A civic routing tool must be calibrated to abstain from answering when confidence is low. Making a low-confidence guess is dangerous; saying "I don't know—please call 311" is the appropriate and safe response. Ultimately, the NYC chatbot was slated to be taken down because it was "functionally unusable" and provided answers that encouraged illegal behavior [3].

## Mitigation approaches used by governments — What to copy vs. avoid
Established patterns in government service tools favor emergency segregation, human fallback, and strict scope gating. 

| Practice | Who/Where | Evidence | What to implement in RVA |
| :--- | :--- | :--- | :--- |
| Immediate emergency transfer | Minneapolis 311 | If a call is deemed an emergency, it is immediately transferred to 911, and the agent stays on the line [1]. | Emergency keyword gate; one-tap "Call 911" UX and transfer guidance. |
| "Not for emergencies" scope limits | Toronto 311 | Live Agent chat explicitly states it is not appropriate for crisis situations and users should always call 9-1-1 for emergencies [14]. | Prominent, persistent banner across the tool. |
| Scope gating + disclaimers | NYC MyCity chatbot | Added stronger disclaimers, but the bot still provided wrong answers and was eventually killed [13] [3]. | Do not rely on disclaimers alone; require confidence thresholds and abstention. |

*Takeaway: Disclaimers do not absolve a tool of providing dangerous advice. Richmond must implement hard emergency routing and human fallbacks.*

## Confidence calibration playbook — Thresholds, prompts, and fallbacks
Concrete, testable thresholds reduce harm without sacrificing utility. The system must be designed to detect out-of-distribution (OOD) queries and handle them gracefully.

* **High Confidence (≥0.90):** Route the request, cite the specific RVA.gov source, and display the confidence level.
* **Medium Confidence (0.75–0.89):** Ask 1–2 clarifying questions. If ambiguity persists, offer the top two categories but require resident confirmation.
* **Low Confidence (<0.75):** Abstain. Present a "Please call 311" message with operating hours and offer a callback option.
* **Safety Cues:** If keywords like "gas smell," "gunshots," "fire," or "active water main break" are detected, immediately halt the routing flow and display a prominent "Call 911" or emergency utility contact directive.

## Required safety features for Richmond’s tool — Non-negotiables to launch
A minimal, safe feature set prevents confidently wrong harm and creates auditability. The following features are non-negotiable for launch:
1. **Always-on emergency banner:** Persistent guidance to call 911 for emergencies.
2. **Confidence display:** A brief explanation of the system's confidence in its routing suggestion.
3. **Inline citations:** Links to official RVA.gov pages or documents for every routing suggestion.
4. **Abstain mode:** A default "I don't know—please call 311" response for low-confidence queries.
5. **Human fallback:** A warm handoff to 311 agents, passing along the transcript and collected context.

## Non-negotiable language for any routing suggestion — Tested copy that reduces risk
Plain, precise language sets correct expectations and channels emergencies away from AI guesses.

* **Emergency Banner:** "If this is an emergency (police, fire, or medical), call 911 now. Do not use this tool for emergencies."
* **High-Confidence Route:** "Based on City guidance [Link], this looks like [Category]. We will submit this to [Department]. Track updates here: [Link]."
* **Low-Confidence/Abstain:** "We’re not confident enough to route this automatically. Please call 311 so a person can help, or request a callback. If anyone is in danger, call 911."
* **Safety Cue Detected:** "This may involve a safety risk. For immediate assistance, call 911 now."

## Implementation checklist and measurement plan — Prove safety and value early
To ensure the tool operates safely, Richmond must instrument telemetry from day one to verify abstention rates and harm prevention.

* **Pre-launch:** Seed a lexicon for emergency cues and validate it with RVA 911/311 supervisors. Map the top 20 RVA311 categories to official sources, explicitly flagging boundary seams like DPW vs. DPU.
* **Post-launch (30/60/90 days):** Track the misroute rate, abstention rate, and human escalation rate. Audit random abstentions and high-confidence routes weekly to ensure citation validity and accuracy. Publish a quarterly transparency note detailing metrics and system adjustments.

## References

1. *Building a 311 System: A Case Study of the City of Minneapolis*. https://portal.cops.usdoj.gov/resourcecenter/content.ashx/cops-w0488-pub.pdf
2. *NYC's AI chatbot was caught telling businesses to break the law. The city isn't taking it down | AP News*. https://apnews.com/article/new-york-city-chatbot-misinformation-6ebc71db5b770b9969c906a7ee4fae21
3. *Mamdani to kill the NYC AI chatbot we caught telling businesses to break the law – The Markup*. https://themarkup.org/artificial-intelligence/2026/01/30/mamdani-to-kill-the-nyc-ai-chatbot-we-caught-telling-businesses-to-break-the-law
4. *Water Utility | Richmond*. https://www.rva.gov/public-utilities/water-utility
5. *Potholes and Street Maintenance | Richmond*. https://www.rva.gov/public-works/potholes-and-street-maintenance
6. *Location-Based Routing for Wireless 911 Calls Report and ...*. https://docs.fcc.gov/public/attachments/DOC-399578A1.pdf
7. *Blackhole to Beacon: Real-Time 311 Service – CivicPlus*. https://www.civicplus.com/blog/crm/inside-the-digital-request-from-blackhole-to-beacon/
8. *Richmond sinkhole reveals water main leak threatening Henrico’s water supply*. https://www.wtvr.com/news/local-news/henrico-water-supply-richmond-sinkhole-may-30-2025
9. *311 Coordinator - Civilized.ai*. https://civilized.ai/311-coordinator
10. *
	
		
		








  
Service Request Status · NYC311
*. https://portal.311.nyc.gov/article/?kanumber=KA-01066
11. *New York City defends AI chatbot that advised entrepreneurs to break laws | Reuters*. https://www.reuters.com/technology/new-york-city-defends-ai-chatbot-that-advised-entrepreneurs-break-laws-2024-04-04/
12. *NYC's AI Chatbot Tells Businesses to Break the Law*. https://themarkup.org/artificial-intelligence/2024/03/29/nycs-ai-chatbot-tells-businesses-to-break-the-law
13. *Malfunctioning NYC AI Chatbot Still Active Despite Widespread Evidence It’s Encouraging Illegal Behavior | THE CITY — NYC News*. https://www.thecity.nyc/2024/04/02/malfunctioning-nyc-ai-chatbot-still-active-false-information/
14. *Using 311 Live Agent Support – City of Toronto*. https://www.toronto.ca/home/311-toronto-at-your-service/live-agent-service/