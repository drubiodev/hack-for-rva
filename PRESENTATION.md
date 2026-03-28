# ContractIQ — 6-Minute Presentation Script

> **Format:** Live demo + narration. No slides required.
> **Timing:** ~6 minutes total. Keep demo moving — don't linger.

---

## 1. The Problem (60 sec)

> *"Every week, Richmond procurement staff open dozens of PDFs — contracts, RFPs, amendments — and manually hunt for expiration dates, vendor terms, and compliance flags. There's no dashboard. No early warning. Just staff eyes on paper.*
>
> *One missed renewal window can cost the City tens of thousands of dollars or trigger a compliance violation. We asked: what if AI could do that first pass for you?"*

---

## 2. What We Built (30 sec)

> *"ContractIQ is a procurement intelligence dashboard for City staff. Upload any contract PDF — the system reads it, extracts the key fields, flags the risks, and puts it in a review queue — in under 60 seconds."*

---

## 3. Live Demo (3 min)

| Step | What to show | Say |
|---|---|---|
| **Upload** | Drag a PDF onto the upload zone | *"Staff drop in a contract — could be a scan, a fax, anything."* |
| **Processing** | Watch the floating queue tracker tick through stages | *"Azure Document Intelligence does the OCR. GPT-4o mini classifies it and extracts vendor, value, dates, department."* |
| **Document view** | Click into the processed doc, show extracted fields + validation flags | *"It found 2 flags — expiration is in 47 days, and the vendor name doesn't match the signature block."* |
| **Chat** | Ask "Which contracts are expiring this quarter?" | *"And staff can query across all contracts in plain English. Real City of Richmond data, 1,362 contracts."* |
| **Dashboard** | Show KPIs + document queue | *"Everything lands in a live queue with status tracking through analyst review to supervisor approval."* |

---

## 4. How It Works (45 sec)

> *"Under the hood: Azure Document Intelligence for OCR, Azure OpenAI for extraction and the RAG chatbot, Azure AI Search indexing all contract text, FastAPI backend, Next.js dashboard — all running on Azure Container Apps. We ingested real Richmond contract data from the City's open data portal day one."*

---

## 5. Impact (30 sec)

> *"Today a procurement analyst spends roughly 20 minutes manually reviewing a single contract. ContractIQ gets it to a structured, flagged, searchable record in under a minute. For a city managing 1,300+ active contracts, that's not a small win — that's a different way of working."*

---

## 6. Close (15 sec)

> *"We built this in 48 hours on real City data to show what's possible. The infrastructure is live, the AI is answering real questions. ContractIQ — smarter procurement for Richmond."*

---

## 7. Cost (if asked / bonus time — 30 sec)

> *"The entire stack costs less than a rounding error on a City contract. We ran this hackathon on roughly $65 in Azure credits — OCR, AI extraction, search, hosting included. At production scale for Richmond's contract volume, we estimate under $200/month. Compare that to one hour of a procurement analyst's time."*

| Service | What it does | Est. monthly cost at scale |
|---|---|---|
| Azure Document Intelligence | OCR / reads PDFs | ~$15 per 1,000 pages |
| Azure OpenAI (GPT-4o mini) | Extraction + chat | ~$0.15 per 1M tokens |
| Azure AI Search | Contract search index | ~$25 (Basic tier) |
| Azure SQL | Structured contract data | ~$15 (S0 tier) |
| Azure Container Apps | Hosts frontend + backend | ~$10–30 (consumption) |
| **Total** | | **~$65–100/month** |

---

## 8. Next Steps (if time allows — 45 sec)

> *"We built the foundation in 48 hours. Here's what a real deployment looks like:"*

**Short term (weeks)**
- Connect directly to Richmond's existing contract repository — no manual upload needed
- Role-based access (analyst vs. supervisor views already scaffolded)
- Email/Teams alerts when a contract enters its renewal window

**Medium term (months)**
- Ingest VITA and GSA contract listings for side-by-side cost comparison
- Auto-suggest better purchasing options when a contract is flagged as expensive
- Audit trail and approval history for procurement compliance reporting

**Long term (vision)**
- City-wide procurement intelligence: every department sees their contracts, risks, and savings opportunities in one place
- Integration with Richmond's budget system to tie contracts to appropriations
- Expand to other document types: grants, MOUs, insurance certificates

> *"The hardest part — getting AI to reliably read and understand City contracts — is already working. Everything else is configuration and integration."*

---

## Pre-Demo Checklist

- [ ] Backend running at `http://localhost:8000` (or deployed Azure URL)
- [ ] Dashboard open in browser on the document queue page
- [ ] At least one document already processed with flags visible
- [ ] Chat panel tested — have a cached answer ready if response is slow
- [ ] Know which PDF you're uploading live (use `Insight Public Sector` or `Simons Contracting`)

## Tips

- **Don't read from this doc** — talk to the judges, point at the screen
- The document detail page with red flags is the money shot — land there fast
- If the live upload takes too long, skip to a pre-processed document
- Lead with the problem, not the tech — judges care about Richmond, not Azure
