# Procurement Contract Examples

## What this is

Ten real City of Richmond procurement contracts, provided as sample material for hackathon teams working on the **Procurement Risk Review** problem statement (Problem 2 in this pillar).

The PDFs are image-scanned originals. The `.txt` files are OCR-extracted text versions, generated using tesseract at 144dpi, suitable for LLM input, keyword search, and automated term extraction.

---

## Why these exist

City staff currently review procurement contracts by manually scanning PDFs across multiple sources — the City Contracts Socrata dataset, VITA state contracts, SAM.gov federal contracts, and eVA. Key details like expiration dates, renewal windows, contract amounts, and vendor terms are buried in documents like these.

The hackathon challenge is to build a tool that surfaces those details automatically — so staff spend less time reading PDFs and more time making decisions.

These contracts are the raw material. Teams can use them to:
- Build and test PDF extraction pipelines
- Train a key-term extractor (expiration dates, amounts, renewal clauses, contract type)
- Demonstrate a "contract risk dashboard" prototype with real document content
- Show plain-language summaries of complex contract language

---

## The contracts

| File | Vendor | Service area | Year |
|------|--------|--------------|------|
| Contract 20000003712 | ATAB LLC dba Dominion Elevator Services | Elevator inspection services | 2019 |
| Contract 21000000131 | Colony Construction / Lee Hy Paving / A&A Contractors (multi-award) | Road and construction | 2020 |
| Contract 22000008081 | CliftonLarsonAllen LLP | Audit services | 2022 |
| Contract 22000011432 | Addo Enterprises Inc | Services contract | 2022 |
| Contract 23000004767 | Jeffrey Stack Inc. dba JSI Paving | Paving and construction | 2022 |
| Contract 23000012317 | Vision Government Solutions Inc | Government software/assessment | 2023 |
| Contract 24000006048 | Insight Public Sector | IT / technology | 2023 |
| Contract 24000012493 | Corvel Enterprise Comp Inc | Workers' compensation management | 2024 |
| Contract 25000005766 | Simons Contracting Co Inc | Construction/maintenance | 2024 |
| Contract 25000012048 | Insight Public Sector + Flock Group Inc | Technology services | 2025 |

---

## Data format

Each contract has two files:

- **`.pdf`** — the original scanned document
- **`.txt`** — OCR-extracted plain text, page-separated with `--- Page N [OCR] ---` markers

The `.txt` files are ready to paste into an LLM prompt, index with a vector store, or feed into a key-term extraction pipeline.

One contract (24000012493) was a text-based PDF rather than a scanned image — its `.txt` is extracted directly and will be cleaner than the OCR files.

---

## Known limitations of the OCR output

- Handwritten signatures and dates scan poorly — expect garbled text around signature blocks
- Some contracts have bleed-through from reverse pages — occasional noise in the extracted text
- Tables may not preserve column alignment — extract structured fields by pattern matching rather than position
- OCR confidence varies by scan quality — cross-check any dollar amounts or dates against the original PDF before citing them

---

## What to build with these

**A procurement key-term extractor** — given a PDF or text file, return:
- Contract number
- Vendor name
- Contract type (goods and services, construction, IDIQ, etc.)
- Maximum contract amount
- Commencement date
- Expiration / renewal date
- Department
- Key compliance clauses

**A contract risk dashboard** — visualize:
- Contracts approaching expiration (next 30 / 60 / 90 days)
- Contracts without a documented renewal option
- Contracts above a dollar threshold requiring additional review
- Vendor concentration (multiple contracts with the same vendor)

**A plain-language contract summary tool** — take a contract PDF, return a 200-word plain-language explanation of what the City is buying, from whom, for how much, and for how long.

---

## Where the structured data lives

The City Contracts open dataset (Socrata `xqn7-jvv2`) is the structured complement to these PDFs. It contains ~1,362 rows of contract metadata. Use it for the dashboard layer and the PDFs for the extraction/summarization layer.

**Important:** The Socrata SODA API for this dataset has a known bug returning only 8 of 9 columns. Use the CSV download instead:
```
https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD
```

For federal cross-referencing via SAM.gov: non-federal users without a registered role are limited to **10 API requests per day**. Pre-compute and cache any SAM.gov lookups — do not make live calls during your demo.

---

## Constraints

- Do not make legal compliance determinations — surface information for staff review only
- Do not claim your tool represents official City procurement records
- Label all extracted data as "extracted from document" and note that manual verification is required for any binding decision
