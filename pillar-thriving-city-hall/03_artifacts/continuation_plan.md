# Post-Hackathon Continuation Plan — A Thriving City Hall

This document outlines potential pathways for continuing work from the hackathon. Nothing here is a commitment — it describes opportunities that would require formal engagement with City staff and partners.

---

## Problem 1: Resident Service Navigation

### Most likely continuation path
- **Champion contact:** Pete Breil, Director of 311 (Richmond City), is the strongest candidate for a post-hackathon champion on the resident service navigation problem. As of March 2026, his involvement is implicit rather than formally committed.
- **What continuation would require:** A working demo that reduces misrouted requests; evidence of resident confusion from current 311 request patterns; City IT (Office of Information Technology) involvement for any integration with official systems.
- **Near-term next step:** Request a meeting with Pete Breil and the RVA311 team after the hackathon to present the prototype and gather feedback on routing accuracy.

### Partner organizations
- **Code for America (Code for Richmond brigade):** Code for America has deep experience with 311 data, service navigation, and government digital services. A local brigade or CfA national could be a technical partner.
- **AARP Virginia / Digital Literacy organizations:** Digital equity organizations in Richmond could help ensure any resident-facing tool works for low-digital-literacy users.
- **Boaz & Ruth / Richmond community organizations:** Community organizations that help residents navigate City services could serve as distribution channels and user research partners.

### What a continuation would need to maintain
- Ongoing alignment with rva.gov content updates (service descriptions change)
- A feedback mechanism for incorrect routing suggestions
- A human escalation path (link to call 311 or contact staff directly)
- Translation/multilingual support (rva.gov serves 36 languages via Google Translate)

---

## Problem 2: Procurement Contract Review

### Most likely continuation path
- **Champion gap:** As of March 2026, there is no named departmental champion committed to the procurement problem. Post-hackathon continuation would require identifying a champion within City procurement staff (Director of Finance or Chief Procurement Officer's office).
- **What continuation would require:** A working demo that saves measurable staff time; access to a broader sample of contract PDFs for extraction testing; engagement with the City's existing procurement workflow.

### Partner organizations
- **OpenGov:** If the City uses or evaluates OpenGov for procurement, the hackathon tool could complement or inform that evaluation.
- **Code for America (Procurement Team):** CfA has done prior work on government procurement transparency and simplification.
- **Virginia Department of General Services:** The state agency responsible for statewide contracts (including VITA) could be a partner for cross-source contract data.

### What a continuation would need to maintain
- Regular refresh of the City Contracts Socrata data
- Confirming data schema on each refresh (no column bug exists; API returns all 9 columns; corrected 2026-03-18)
- Legal review of any tool claiming to help with compliance determination
- Clear "advisory only" labeling throughout

---

## Artifacts worth preserving regardless of continuation
- The 311 request type taxonomy (if built as part of the hackathon) — a useful artifact for future 311 navigation work
- The contract expiry dashboard data pipeline — can be refreshed periodically from public Socrata data
- Evidence log and data source inventory — valuable reference for any future City Hall civic tech work
- Research prompts and findings — reusable for future hackathons or CfA projects
