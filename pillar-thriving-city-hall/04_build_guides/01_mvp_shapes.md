# MVP Shapes — A Thriving City Hall

Five buildable shapes for this pillar. Choose the one that matches your team's skills and the problem you've selected.

---

## Shape A — Plain-Language Service Finder

### Best for
Teams with NLP, search, or content-design strength.

### Problem it addresses
Resident Service Navigation — residents who can't find the right City service or 311 category.

### Inputs
- rva.gov content (crawled or manually curated subset of department pages)
- 311 request type taxonomy (built from historical data or manual research)
- Plain-language descriptions of common resident situations

### Demo
Resident types "there's an abandoned car in front of my house" → tool returns: correct 311 category, department responsible, and link to submit the official request → vs. the current rva.gov search returning department-centric results.

### Key constraints
- Must link to official RVA311 portal for actual submission — never simulate a submission
- Must show source for every suggestion ("based on rva.gov content last updated...")
- Must include a "not sure? Call 311 at 3-1-1" escape hatch

---

## Shape B — 311 Category Router

### Best for
Teams interested in decision-tree design, logic modeling, and frontend development.

### Problem it addresses
Resident Service Navigation — reducing the wrong-category submission problem in RVA311.

### Inputs
- 311 request type taxonomy (~50+ types across 7 department groups)
- Plain-language category descriptions
- Disambiguation rules for overlapping categories (e.g., pothole vs. water main break)

### Demo
User walks through a 3–5 question decision tree about their situation → receives recommended 311 category with an explanation → sees a link to the official RVA311 portal.

### Key constraints
- Historical Socrata data (vgg4-hjn8) is useful for understanding category patterns but represents 2014–2015 data only
- No live RVA311 data is available; tool must be built on manual category research
- Must clearly label as a guide, not an official submission interface

---

## Shape C — Procurement Contract Expiry Tracker

### Best for
Teams with data wrangling and frontend/visualization skills.

### Problem it addresses
Procurement Risk Review — staff needing a quick view of upcoming contract renewals.

### Inputs
- City Contracts Socrata CSV download (xqn7-jvv2, all 9 columns)
- SAM.gov API (optional stretch: debarment check)
- eVA CSV (optional: state contract comparison)

### Demo
Dashboard loads City Contracts data → filtered view shows 8 contracts expiring in next 60 days → click a contract → see vendor, amount, department, expiry date, and renewal window → vs. manually scanning the full dataset.

### Key constraints
- Use CSV download (not API) to get all 9 columns — the API has a known column bug
- Date normalization may be needed; contract dates can be inconsistently formatted
- Tool is advisory only; staff must verify in official systems before acting

---

## Shape D — PDF Contract Extractor

### Best for
Teams with LLM/document processing skills and a product lead who can scope accurately.

### Problem it addresses
Procurement Risk Review — reducing time to extract key terms from contract PDFs.

### Inputs
- Sample contract PDFs (need to be sourced before or during the hackathon — see VERIFICATION_TODO.md)
- A defined extraction schema: expiration date, renewal option, pricing structure, key conditions

### Demo
Upload a sample contract PDF → tool extracts and displays: expiration date (page 3), renewal window (page 8), pricing term (page 12) → side-by-side with original PDF viewer → vs. manually scrolling through 40 pages.

### Key constraints
- LLM extraction is probabilistic — must always label results as "AI-assisted, requires human review"
- Never claim legal accuracy; always include a disclaimer
- Needs sample PDFs — this is a hard dependency; without them the demo cannot work

---

## Shape E — Government Transparency Dashboard

### Best for
Teams with data visualization skills who want to address both residents and staff audiences.

### Problem it addresses
Cross-cutting — making City spending and contract data more visible and understandable.

### Inputs
- City Contracts Socrata CSV (xqn7-jvv2)
- USASpending.gov API (federal spending by recipient in Richmond)
- Optional: eVA CSV for state-level spending

### Demo
Dashboard with filters for department, vendor, year, and contract type → shows spending trends → click a vendor → see all contracts across City, state, and federal sources → vs. needing to know which portal to check.

### Key constraints
- Must clearly label data sources and refresh dates
- Must not claim to represent official City financial reporting
- Spending data across sources uses different schemas — normalization is the main technical challenge
