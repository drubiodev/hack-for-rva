# Prototype Recommendations — A Thriving City Hall

Six concepts organized by the two targeted problem statements. Each includes feasibility notes for a 48-hour hackathon window.

---

## Problem 1 — Helping Residents Find the Right City Service or Next Step

### Concept A: Plain-Language 311 Helper
- **What it is:** A conversational intake tool where residents describe their problem in plain language and receive the correct 311 category, department, and next step — with a direct link to the RVA311 portal.
- **User served:** Richmond residents who don't know which 311 category applies to their issue.
- **48-hour feasibility:** Build a decision tree or NLP classifier over the ~50 known RVA311 request types; map plain-language descriptions to categories; provide link to official RVA311 portal for actual submission.
- **Data/content:** 311 request type taxonomy (manual research or historical Socrata data); official rva.gov department descriptions; RVA311 submission URL.
- **Team roles:** Product lead (decision logic), frontend dev (UI), UX writer (plain-language mapping), researcher (category verification).
- **Key risk/limitation:** Categories change over time; tool must be clearly labeled as a guide, not an official City interface. Must never claim a submission was made on behalf of the user.
- **Compelling demo:** "My neighbor has been dumping trash in the vacant lot" → tool identifies Illegal Dumping → shows the right category and a link to submit → vs. resident guessing wrong and picking "General Services."

---

### Concept B: RVA.gov Smart Search
- **What it is:** A search interface over rva.gov content that accepts plain-language queries and returns ranked, plain-language results — filling the gap left by Drupal's built-in faceted search.
- **User served:** Residents trying to find the right City service or department using natural language.
- **48-hour feasibility:** Crawl a subset of rva.gov pages (department landing pages, service descriptions); index content with a simple vector search or keyword ranking; present results with plain-language summaries and links to official pages.
- **Data/content:** Crawled rva.gov content (public, no authentication required); Google Translate integration for multilingual support.
- **Team roles:** Backend dev (crawler + search), frontend dev (UI), UX writer (result display), researcher (verification).
- **Key risk/limitation:** Crawled content may be outdated; must clearly show source URLs and "last updated" if available; must not claim to represent official City content.
- **Compelling demo:** "How do I report a broken streetlight?" → smart search returns the right department and form → vs. current Drupal search returning a mix of irrelevant pages.

---

### Concept C: Service Pathway Mapper
- **What it is:** An interactive guide that maps common resident situations (pothole, noise complaint, business license question, etc.) to the correct City service pathway, showing department, channel (website/phone/app), and typical resolution steps.
- **User served:** First-time users of City services who don't know the landscape.
- **48-hour feasibility:** Build a static or semi-static card-based interface with 10–20 common situations; each card links to official City pages; can be enhanced with a simple search or filter.
- **Data/content:** Public rva.gov content; 311 request type list; department contact information.
- **Team roles:** Product lead (situation taxonomy), UX designer, frontend dev, content writer.
- **Key risk/limitation:** Must be clearly labeled as a guide, not an official City interface; must not claim to represent City policy.
- **Compelling demo:** Walk through three different resident situations; show how the mapper routes each one correctly; compare to the current experience of navigating rva.gov alone.

---

## Problem 2 — Helping City Staff Review Procurement Risks and Opportunities

### Concept D: Contract Expiry Dashboard
- **What it is:** A data dashboard that pulls from the City Contracts Socrata dataset (API or CSV download, both return all 9 columns; corrected 2026-03-18) and visualizes contracts by expiration date — with filters for department, vendor, and time window.
- **User served:** City procurement staff needing a quick view of upcoming renewals.
- **48-hour feasibility:** Ingest City Contracts CSV; parse and normalize dates; build a sortable/filterable table or Gantt-style view; highlight contracts expiring within 30/60/90 days.
- **Data/content:** City Contracts Socrata CSV download (xqn7-jvv2); SAM.gov API for debarment cross-check (stretch goal).
- **Team roles:** Data wrangler (ingestion + normalization), frontend dev (dashboard), product lead (filters and UX).
- **Key risk/limitation:** Contract data may have inconsistent date formats; staff must still verify with official systems before acting on dashboard information; tool is advisory only.
- **Compelling demo:** Load the CSV → dashboard shows 8 contracts expiring in the next 30 days → click one → see vendor, amount, department, and renewal window → vs. manually scanning the full spreadsheet.

---

### Concept E: PDF Contract Extractor
- **What it is:** A tool where staff upload a contract PDF and receive an extracted summary of key fields: expiration date, renewal option window, pricing terms, and key conditions — reducing manual scanning time.
- **User served:** Procurement staff who need to extract consistent information from inconsistently formatted contract documents.
- **48-hour feasibility:** Use an LLM or document processing library to extract structured fields from PDF text; display results as a structured summary with source page references; always include a "verify in original document" disclaimer.
- **Data/content:** Sample contract PDFs (need to be sourced before hackathon — see VERIFICATION_TODO.md); no live data dependency.
- **Team roles:** Backend dev (PDF parsing + LLM extraction), frontend dev (upload UI + results display), product lead.
- **Key risk/limitation:** LLM extraction can miss or misread fields; results must always be labeled as AI-assisted and require human review; avoid claiming legal accuracy.
- **Compelling demo:** Upload one sample contract PDF → extracted summary shows expiration date, renewal window, and key terms → show "found on page X" reference → vs. manually scrolling through 40 pages.

---

### Concept F: Cross-Source Contract Finder
- **What it is:** A search tool that queries across the City Contracts Socrata dataset, SAM.gov, and eVA simultaneously to show staff what contracts exist across sources for a given commodity or service type.
- **User served:** Procurement staff evaluating whether to use City contracts, state contracts (VITA), or federal schedules (GSA) for a purchase.
- **48-hour feasibility:** Connect to City Contracts CSV + SAM.gov API (free key) + eVA CSV; build a unified search by keyword or commodity code; display results by source with key fields.
- **Data/content:** City Contracts CSV; SAM.gov API (requires key registration before hackathon); eVA CSV; VITA web (stretch goal, scraping required).
- **Team roles:** Data wrangler (multi-source ingestion), backend dev (unified search), frontend dev (results UI), product lead.
- **Key risk/limitation:** Data schemas differ across sources; staff must confirm contract validity before use; tool is a discovery aid, not a compliance determination.
- **Compelling demo:** Search "janitorial services" → see City contract (expires 2026-08), VITA state contract (expires 2027-01), and SAM.gov listing → compare pricing and terms side by side.
