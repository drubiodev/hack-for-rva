# Targeted Problem Statements — A Thriving City Hall

---

## 1) Helping Residents Find the Right City Service or Next Step

Score: 27/32 — Strong

### Problem statement
How might we use technology to help Richmond residents quickly determine the right next step when interacting with City services — whether finding information or submitting a request — so that issues are routed correctly the first time while working within existing City systems and minimizing additional staff workload?

### Context
Residents come to rva.gov or RVA311 with a real need but may not know which department handles the issue, which request type applies, or whether they need information, a form, or a service request. City information is spread across multiple pages and systems, and residents struggle to determine what is current, relevant, or authoritative.

When people cannot find the right path, they submit the wrong request type, contact staff directly, or abandon the process. The City's information architecture is department-centric rather than citizen-centric. Website search is often ineffective, request categories overlap, and citizens submit requests even when no clear category fits.

### Constraints
- Must work with existing City systems (rva.gov and RVA311) — not replace them
- Must rely on verified City information only
- Must avoid confidently answering when information is unclear, outdated, or conflicting
- Must reduce staff burden rather than increase it
- Must respect current system and data limitations
- Must not claim to be an official City service or to represent City determinations

### Success would mean
- Residents can describe their issue in plain language and receive the right next step
- More requests are routed correctly the first time
- Fewer residents are forced to guess which category or department applies
- Staff spend less time redirecting routine inquiries
- The City gains insight into where website content and service pathways are failing

### Critical data constraints
- **No post-2018 RVA311 open data.** The Socrata 311 dataset (vgg4-hjn8) contains SeeClickFix data from January 2014–August 2015 only.
- **AvePoint Citizen Services platform** (launched June 15, 2018) does not publish to Socrata and exposes **no public API**.
- **2025 volume:** 208,216 total RVA311 requests (reported figure — see VERIFICATION_TODO.md).
- **~50+ request types** across 7 department groups in the current RVA311 system.

### Technical landscape

**rva.gov**
- Platform: Drupal 8+ on Acquia, developed by Tech Dynamism
- Search: Drupal Search API with Facets module
- Search URL pattern: `https://www.rva.gov/search?search={query}&page={n}&f[0]=business_unit:{id}`
- Over 40 department slugs
- Translation: Google Translate widget (36 languages)

**RVA311**
- Platform: AvePoint Citizen Services on Dynamics 365
- Launched: June 15, 2018
- Built on Microsoft Dynamics 365 and Azure
- 2025 volume: 208,216 total requests (unverified — see VERIFICATION_TODO.md)
- ~50+ request types across 7 department groups
- No public API

**Integration chain**
- Citizen → RVA311 (Dynamics 365) → Microsoft BizTalk → Trimble Cityworks (DPW work orders)

**Historical Socrata Dataset (vgg4-hjn8)**
- Contains SeeClickFix data only: January 2014–August 2015
- SODA API: `data.richmondgov.com/resource/vgg4-hjn8.json`
- Not representative of current 311 request volumes or categories

### Gaps to close before hackathon
- Name a departmental champion (Pete Briel, Director of 311, is a candidate — not yet formally committed)
- Document the 311 routing decision logic (which categories map to which departments)
- Verify rva.gov sitemap availability and structured data
- Specify expected prototype output type for demo

---

## 2) Helping City Staff Review Procurement Risks and Opportunities

Score: 22/32 — Needs work

### Problem statement
How might we use technology to help Richmond staff identify valid, compliant, and cost-effective purchasing contracts across City, state, and federal sources so that procurement decisions require less manual review while maintaining legal compliance and transparency?

### Context
City staff rely on multiple contract sources: City contracts, state (VITA) contracts, federal (GSA) contracts, and cooperative purchasing agreements. Key details — expiration dates, renewal windows, pricing terms, and contract conditions — are often buried in PDFs or spread across different systems.

There is currently no unified view of upcoming renewals, no easy way to extract key terms from contract documents, and no simple comparison tool across City, state, and federal sources. Staff must manually scan PDFs and databases to gather the information needed to make informed procurement decisions.

### Constraints
- Must comply with procurement law and City procurement policies
- Must support staff judgment rather than replace it
- Must work with existing contract repositories and document formats
- Must use publicly available or City-accessible contract information
- Must be scoped tightly enough for a weekend prototype
- Must not make legal compliance determinations or contract award decisions

### Success would mean
- Staff can more easily see which contracts are expiring or need review
- Key procurement details are easier to extract from existing contract documents
- Departments spend less time manually scanning PDFs and databases
- The City reduces the risk of missed renewals or outdated contract use
- Procurement teams have a clearer early-warning view of upcoming decisions

### Data sources

**City Contracts Socrata (xqn7-jvv2)**
- 9 columns, earliest records ~January 2011
- SODA API: `data.richmondgov.com/resource/xqn7-jvv2.json` — **NOTE: API returns only 8 columns (known bug)**
- CSV with all 9 columns: `data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD`
- Use the CSV download to get all columns

**SAM.gov**
- Federal System for Award Management
- Free API key required
- Covers federal contracts and debarment data

**eVA (Virginia electronic procurement)**
- Statewide procurement data on data.virginia.gov
- CSV export available

**VITA statewide contracts**
- Virginia IT Agency contract listing
- URL: `vita.cobblestonesystems.com/public/`
- Web only — no API

**GSA Schedules**
- Federal supply schedules accessible via SAM.gov

### Known gaps
- Sample procurement PDFs not pre-staged (needed for PDF extraction demos)
- No named departmental champion committed to this problem
- Procurement workflow is undocumented (how staff currently navigate across sources)
- VITA contract portal has no API — scraping or manual extraction required

### Gaps to close before hackathon
- Pre-stage 5–10 representative contract PDFs for extraction demos
- Name a departmental champion from City procurement staff
- Document the current staff workflow for contract review
- Clarify what "compliance check" means in practice for a demo scenario
