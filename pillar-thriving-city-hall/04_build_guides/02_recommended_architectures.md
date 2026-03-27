# Recommended Architectures — A Thriving City Hall

For each MVP shape, a realistic weekend-feasible architecture with stack notes and feasibility assessment.

---

## Shape A — Plain-Language Service Finder

### Recommended stack
- **Frontend:** React or plain HTML/CSS + JavaScript (keep it simple for a weekend)
- **Backend (optional):** Python Flask or FastAPI if you need a search API layer; can be static if you pre-index
- **Search:** Algolia (free tier), Fuse.js (client-side fuzzy search), or a simple vector embedding approach if your team has ML experience
- **Data pipeline:** Python crawler over a curated subset of rva.gov pages; store as JSON; rebuild index manually during hackathon

### Data flow
1. Pre-hackathon (or Friday evening): Crawl ~20–50 key rva.gov pages (department landing pages, service descriptions)
2. Build a JSON index of page titles, descriptions, and 311 category mappings
3. Frontend queries the index with fuzzy/semantic search
4. Return ranked results with plain-language descriptions and links to official pages

### Weekend feasibility
- Feasible: The crawler and static index can be built in a few hours; the frontend is a standard search UI
- Risk: rva.gov content may be stale or inconsistently structured; allow time for manual curation
- Stretch: Add multilingual support via translation API

### Demo setup
- Pre-load the index with 20–30 common resident situations; hardcode a few showcase queries for the live demo
- Have a "fallback" slide showing the before/after of rva.gov search vs. your tool

---

## Shape B — 311 Category Router

### Recommended stack
- **Frontend:** React or plain HTML/CSS with a decision-tree component library
- **Logic:** Hard-coded decision tree in JSON or a simple rule engine; no ML required
- **Data:** 311 category taxonomy built manually from public information and historical Socrata data (vgg4-hjn8)

### Data flow
1. User selects or describes their situation
2. Decision tree traverses to the correct category node
3. Return: recommended 311 category + plain-language explanation + link to official RVA311 portal

### Weekend feasibility
- Highly feasible: Decision trees are deterministic and easy to build and demo
- Risk: Category taxonomy research takes time; budget Friday evening for this
- The ~50 RVA311 categories can be manually mapped over a few hours using public rva.gov content

### Demo setup
- Build 3–5 specific scenarios end-to-end (pothole, illegal dumping, abandoned vehicle, noise complaint, broken streetlight)
- The demo is the contrast between guessing in the RVA311 dropdown vs. being guided to the right answer

---

## Shape C — Procurement Contract Expiry Tracker

### Recommended stack
- **Frontend:** React with a table component (React Table, Tanstack) or a simple D3/Chart.js timeline
- **Data:** City Contracts CSV download (no server needed if processing client-side; use Papa Parse for CSV parsing)
- **Backend (optional):** Python + pandas for preprocessing; output a cleaned JSON file; serve statically

### Data flow
1. Download City Contracts CSV (all 9 columns)
2. Parse and normalize dates; calculate days-to-expiry
3. Build a sortable/filterable table or Gantt view
4. Filter for contracts expiring in 30/60/90 days

### Weekend feasibility
- Highly feasible: This is primarily a data wrangling + table/chart problem
- Risk: Date format inconsistencies in the Socrata data; budget time for normalization
- Stretch: Add SAM.gov debarment cross-check (requires API key registration)

### Demo setup
- Load a cleaned version of the CSV; apply a "next 60 days" filter; show 5–8 contracts in the danger zone
- Click one to show the detail view: vendor, amount, department, dates

---

## Shape D — PDF Contract Extractor

### Recommended stack
- **Frontend:** Simple file upload form + results display (React or plain HTML)
- **Backend:** Python with pypdf or pdfminer for text extraction; OpenAI/Anthropic API for structured extraction
- **Prompt strategy:** Provide the contract text (or excerpts) to the LLM with a structured output schema (JSON with fields: expiration_date, renewal_option, pricing_term, key_conditions)

### Data flow
1. User uploads PDF
2. Backend extracts text from PDF (handle both text-layer and scanned PDFs differently)
3. LLM receives text chunks + extraction schema
4. Results displayed as structured card with page references
5. Disclaimer prominently shown: "AI-assisted extraction — verify against original document"

### Weekend feasibility
- Feasible with caveats: LLM extraction is quick to implement; the hard part is robustness across different contract formats
- Risk: Without pre-staged sample PDFs, you cannot test or demo this reliably. This is the critical dependency.
- Recommendation: Source 3–5 sample contract PDFs before or on the first day of the hackathon

### Demo setup
- Use hardcoded sample PDFs for the demo; don't rely on live upload working perfectly
- Show the "before" (40-page PDF) and the "after" (extracted summary in 10 seconds)

---

## Shape E — Government Transparency Dashboard

### Recommended stack
- **Frontend:** React + Recharts or D3.js for visualizations; or Observable if your team prefers notebooks
- **Data:** City Contracts CSV + USASpending.gov API (no key needed) + eVA CSV
- **Backend (optional):** Python to join and normalize data across sources; output as static JSON

### Data flow
1. Ingest City Contracts CSV + USASpending JSON (Richmond city/county) + eVA CSV
2. Normalize vendor names (fuzzy matching), dates, and amounts
3. Build visualizations: spending by department, top vendors, contract expiry timeline, year-over-year trends
4. Filter by department, vendor, year, contract type

### Weekend feasibility
- Feasible: Standard data viz project; the challenge is data normalization across sources
- Risk: Vendor name normalization is notoriously hard; budget time or scope it out for the demo
- Stretch: Add SAM.gov cross-reference; show "this vendor also has $X in federal contracts"

### Demo setup
- Pre-process and normalize the data before the live demo; load from static JSON
- Highlight 2–3 interesting findings (e.g., vendor with most contracts, department with most expiring, year-over-year trend)
