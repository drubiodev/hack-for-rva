# User Journey Maps — A Thriving City Hall

Note: Journeys include plausible observations based on the problem statements and system descriptions in this repository. Each friction point should reference an `evidence_log.md` entry when verified with an official source.

---

## Journey 1 — Resident submitting a service request for a pothole or illegal dumping

**User goal:** Report a neighborhood problem (pothole, illegal dumping, abandoned vehicle) and have it resolved.

**Starting point:** Resident notices the problem and wants to report it to the City.

**Steps taken:**
1. Types a description into Google or goes directly to rva.gov to find out who to contact
2. Searches rva.gov — finds multiple pages across different departments; results are not clearly ordered by relevance
3. Navigates to the RVA311 portal or app to submit a request
4. Encounters ~50+ request types organized by department rather than by plain-language description of the problem
5. Selects a category that seems closest — but may be wrong (e.g., choosing "Street Maintenance" instead of "DPW – Pothole" or picking the wrong department entirely)
6. Submits the request; receives a confirmation number but no clear explanation of next steps
7. Hears nothing for several days; calls 311 directly to follow up
8. Staff manually re-routes the request to the correct department, adding delay

**Pages/systems touched:** Google, rva.gov, RVA311 (AvePoint/Dynamics 365)

**Friction points:**
- rva.gov search results are not organized by citizen need; they reflect department structure
- 311 request types overlap and use departmental jargon rather than plain-language descriptions
- No plain-language "what is your problem?" entry point before category selection
- Residents receive no feedback on whether they selected the right category
- Misrouted requests require manual staff intervention to re-route
- Multi-language residents face additional friction (Google Translate widget exists but quality varies)

**User questions at each step:**
- Is this a 311 issue or should I call a specific department?
- What category should I pick for a pothole that might also be a water leak?
- Did I submit to the right place, or will someone tell me if I didn't?
- Why haven't I heard anything — is my request lost?

**Prototype opportunities:**
- Plain-language intake form ("describe the problem in your own words") that maps to the correct 311 category
- "Before you submit" guide that helps residents distinguish between information requests and service requests
- Category disambiguation tool that shows which department handles overlapping issues
- Confirmation experience that sets accurate expectations about timeline and next steps

---

## Journey 2 — City procurement staff reviewing upcoming contract renewals

**User goal:** Identify which contracts are expiring in the next 90 days, review key terms, and flag any that need action.

**Starting point:** Procurement officer receives a reminder that several contracts are approaching renewal windows.

**Steps taken:**
1. Logs into the City's procurement system (Oracle RAPIDS or equivalent) to pull contract records
2. Exports or downloads contract data; finds expiration dates in the City Contracts Socrata dataset or internal systems
3. Opens the first contract PDF — a complex document with pricing terms, renewal conditions, and compliance requirements buried in appendices
4. Manually searches the PDF for "renewal," "expiration," "option period," and similar terms
5. Records key dates and terms in a spreadsheet
6. Repeats the process for each contract — may have 10–30 to review in a cycle
7. Also checks VITA statewide contract portal to see if any City contracts could be replaced by cheaper state contracts
8. Manually navigates VITA's web-only interface; no API or export function
9. Considers checking SAM.gov for federal GSA schedules as additional options
10. Assembles findings in a summary document for supervisor review

**Pages/systems touched:** Internal procurement system, City Contracts Socrata, contract PDFs, VITA web portal, SAM.gov, spreadsheet

**Friction points:**
- No single dashboard showing all contracts expiring within a user-specified window
- Contract PDFs are inconsistently formatted — key terms are in different locations across vendors
- VITA portal is web-only with no export or API; manual browsing required
- No automated way to compare City contract prices against VITA or GSA equivalents
- Risk of missing renewal windows if the procurement officer is out or the process is manual
- Socrata API returns all 9 columns correctly — no column bug exists; both API and CSV are usable (corrected 2026-03-18)

**User questions at each step:**
- Which contracts expire in the next 60–90 days?
- Is the renewal window still open, or have we passed it?
- What are the key pricing terms and volume commitments?
- Is there a cheaper state (VITA) or federal (GSA) equivalent we should evaluate?
- Are any of our vendors currently debarred from federal contracts?

**Prototype opportunities:**
- Contract expiry dashboard: Socrata data → expiration date filter → sortable list with key fields
- PDF contract extractor: upload a contract → extract and display key dates and terms
- Cross-source contract finder: query across City Socrata + SAM.gov + eVA for similar contract types
- Debarment checker: cross-reference vendor list against SAM.gov exclusions data
