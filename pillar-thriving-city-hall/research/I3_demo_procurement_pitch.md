# Winning a Civic Hackathon Demo with a Procurement Tool

## Executive Summary
Procurement tools face a unique hurdle at civic hackathons: their value is massive, but their interfaces are inherently less intuitive than resident-facing apps. To win a share of the $14,000 prize pool at the Richmond Civic Hackathon [1], your demo must translate back-office administrative friction into tangible, judge-visible impact. 

By leveraging Richmond's official City Contracts dataset, you can expose the hidden risks of manual contract management. The data reveals multi-million-dollar agreements—such as a $29.7 million waste management contract—relying on administrative extensions embedded in text descriptions [2]. Your winning strategy is to visualize this risk immediately, map your presentation directly to the Devpost judging criteria (Impact, Creativity, Feasibility, Prototype Quality, Clarity) [1], and present a tightly scoped 4-minute live demo. By acknowledging data quirks and framing your tool as an advisory layer that complements the City's existing Procurement Transparency Dashboard [3], you can turn the lack of a named City champion into a collaborative proposal aligned with Mayor Avula's "Thriving City Hall" initiative [4].

## Why Procurement Demos Can Win in Richmond—If You Frame Them Right
Resident-facing demos are intuitive; procurement is not. To bridge this gap, you must lead with risk, dollars, and time saved. The Richmond Civic Hackathon is explicitly aligned with Mayor Danny Avula's Action Plan, specifically the "Thriving City Hall" track, which calls for better tools, data transparency, and service delivery [1] [4]. 

When you show a spreadsheet with unsorted dates alongside a $24.6 million security contract or an $80 million healthcare agreement [2], the stakes become instantly legible. A missed renewal equals service disruption and financial risk. By framing your tool as a safeguard against these risks, you transform a dry B2B workflow into a compelling civic safety net.

## What Judges Value—and How Your 4-Minute Arc Maps to the Rubric
Judges at the Richmond Civic Hackathon will evaluate projects based on five specific criteria: Impact on the Richmond community, Creativity and innovation, Feasibility and real-world usefulness, Quality of the prototype, and Clarity of the presentation [1]. Your demo arc must hit every single one of these beats.

* **Impact & Clarity (Hook & Problem):** Opening with the cost of missed renewals and visualizing the manual process proves you understand the real-world stakes.
* **Prototype Quality (Solution):** Showing a working dashboard filtering real data or extracting text from a PDF demonstrates technical execution.
* **Feasibility (Advisory Signal):** Stating that staff still verify against official systems shows you understand governance and aren't overpromising.
* **Creativity (Cross-Source/Extractor):** Pulling in external data from SAM.gov or eVA shows innovative thinking beyond the provided dataset.

## Data Provenance That Builds Trust: xqn7-jvv2, Dashboard, and Cadence
Data provenance is a credibility checkpoint you must clear in the first 20 seconds of your pitch. If judges doubt your data, they will stop listening to your solution. 

The City of Richmond provides the "City Contracts" dataset (identifier: xqn7-jvv2) via its Open Data Portal, updated monthly by the Department of Procurement [3]. It contains exactly nine columns: Agency/Department, Contract Number, Contract Value, Supplier, Procurement Type, Description, Type of Solicitation, Effective From, and Effective To [3]. Put "Source: data.richmondgov.com/xqn7-jvv2 (monthly)" on your screen and say it out loud. Furthermore, mention that the City already has a Procurement Transparency Dashboard [3] —this proves you have done your homework and are building an extension of their current efforts, not replacing them.

### Source Access and Reliability—API vs CSV vs Portal
While Socrata provides an API, live demos are notoriously vulnerable to schema drift, typing quirks, and Wi-Fi failures. The dataset's text descriptions often contain critical lifecycle updates that desync from the official "Effective To" date [2]. For the live pitch, default to a downloaded CSV for absolute stability, but keep your API integration code visible in your GitHub repository to prove technical competence.

## Demo Architecture Options—Pick One Primary, Keep Two as Backups
A single-task flow beats a feature tour for procurement. Choose one primary module to demo live, and keep the others as pre-recorded video fallbacks (the hackathon recommends 2-3 minute demo videos anyway [1]). 

### Comparison: Which Module Scores Best on "Wow," Feasibility, and Risk

| Module | 10-Second "Wow" Factor | Feasibility (Weekend Build) | Failure Modes (What to Say) | Data Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **Expiry Dashboard** | Medium-High | High | Date parsing errors; thin data fields | xqn7-jvv2 CSV [3] |
| **PDF Extractor** | High | Medium | Multiple dates confusing OCR; page anchors failing | Sample contract PDFs |
| **Cross-Source Finder** | Medium | Medium | Rate limits; inconsistent schemas across portals | City dataset + SAM.gov [5] + eVA [6] |

*Takeaway: The Expiry Dashboard is the safest and most reliable live demo. The PDF Extractor and Cross-Source Finder add massive creativity points but carry higher technical risk, making them ideal for pre-recorded video segments.*

## The 4-Minute Script—Procurement Demo Arc With Timestamps
Time discipline is make-or-break. Rehearse this exact 4-minute script to ensure you hit every Devpost rubric requirement without rushing.

* **Opening hook (0:00 - 0:30):** "City staff manually track contract renewals by scanning PDFs and spreadsheets. Last year, multi-million dollar contracts required administrative extensions just to pay invoices. There's a better way."
* **Problem visualization (0:30 - 1:15):** Show the manual process. Display a chaotic CSV spreadsheet with 200 rows of unsorted dates, or a 40-page contract PDF with the expiration date buried in a paragraph on page 27.
* **Solution in action (1:15 - 2:45):** "Here is our dashboard." Click a filter for "next 60 days." Show the UI instantly highlight 8 expiring contracts. Click on one high-value contract to reveal the vendor, amount, department, and dates. *(Optional: If using the extractor, upload a PDF and show the 10-second summary extraction).*
* **"Advisory only" signal (2:45 - 3:05):** "This tool is advisory only. Staff still verify against official systems before acting. We surface the information; they make the decision."
* **Data provenance (3:05 - 3:25):** "This uses Richmond's public City Contracts dataset—openly available at data.richmondgov.com, updated monthly."
* **Impact and ask (3:25 - 4:00):** "What would it take to deploy this? Access to more contract documents and a 30-minute meeting with the procurement team to pilot this alongside their existing Transparency Dashboard."

## Build for Messy Reality—Known Quirks, Risks, and Fallbacks
Real civic data is messy. The Richmond City Contracts dataset frequently embeds critical contract amendments directly into the "Description" field rather than updating the "Effective To" column. For example, a $29.7 million Waste Management contract notes: "*Administrative extension to pay old invoices* Contract expired on 30JAN25" [2]. 

Own these caveats during your pitch. Acknowledge that dates can mislead and that your tool is designed to flag these anomalies for human review. Have fallbacks ready: a pre-recorded video of the PDF extractor, an offline CSV loaded into your app, and a printed one-pager of your UI.

## Q&A You Will Get—Concise Answers With Proof Points
Judges will probe the feasibility and reality of your solution. Use these crisp, cited answers to defuse scrutiny and buy time for your closing argument.

| Judge Question | Crisp Answer + Proof Point |
| :--- | :--- |
| **"Is this using real Richmond data?"** | Yes—the official City Contracts dataset (xqn7-jvv2), updated monthly with 9 fields. The source link is on our screen [3]. |
| **"What's the catch?"** | Two things: API schema quirks (we used the CSV today for stability), and contract extensions are often buried in text descriptions rather than date fields [2]. The tool is advisory; staff verify. |
| **"How would staff actually use this?"** | As a weekly review tool. They filter for the "next 60 days," drill down into the source link, and use the cross-source search to spot alternative vendors. |
| **"Does this duplicate City systems?"** | No. It complements the City's existing Procurement Transparency Dashboard [3] by adding proactive renewal surfacing and cross-source search capabilities. |
| **"What's needed to pilot?"** | Access to a batch of real contract PDFs, a 30-day sandbox environment, and a meeting with the Procurement and Open Data teams. |

*Takeaway: Short, confident answers that reference official City portals prove you are building a feasible, integration-ready prototype.*

## Turning "No Named Champion" Into Momentum
A common weakness in procurement hacks is the lack of a specific City official asking for the tool. Turn this into an inclusive ask. Anchor your project directly to the "Thriving City Hall" track of the Mayor's Action Plan [4]. 

Position your prototype as a lightweight add-on to the City's existing transparency initiatives, not a heavy new system of record. Your direct ask at the end of the pitch should be a 30-to-60-day pilot using additional contract documents, framed as a way to amplify the Department of Procurement's ongoing work.

## Make the Invisible Visual—Before/After Patterns That Land
To make back-office work visual, rely heavily on split-screens and clear badging. Show the "Before" (CSV chaos or a dense PDF page) immediately next to the "After" (a clean 60-day filter highlight or extracted fields). 

If you built the cross-source finder, demo a search for "janitorial services" and clearly label the results with visual badges: "City" (Richmond data), "State" (eVA portal) [6], and "Federal" (SAM.gov) [5]. This proves real-world utility beyond a single dataset and shows how staff could easily find alternative vendors.

## Conservative Impact Claims You Can Defend
Do not over-claim savings. Instead, use actual dataset examples to imply the stakes. Cite visible, large contracts from the CSV—such as the $29.7M Waste Management contract, the $24.6M Top Guard security contract, or the $80M CIGNA healthcare agreement [2]. State simply: "Catching even one high-value renewal early can avoid emergency extensions and price risk. This tool reduces manual scanning time and surfaces deadlines proactively."

## Appendix—Links, Queries, and Setup Checklist
Reduce demo risk by having all assets pre-loaded and cached before you step on stage.
* **Links to keep open in tabs:** City Contracts (xqn7-jvv2) [3], Procurement Transparency Dashboard [3], SAM.gov Contract Opportunities [5], eVA portal [6].
* **Prepared assets:** The downloaded CSV snapshot, one "hero" contract pre-selected (e.g., Waste Management), one 40-page PDF ready to upload, and your 2-3 minute backup video [1].
* **Pre-set Filters:** Have your dashboard pre-filtered to show `effective_to` within the next 60 days, with columns restricted to Vendor, Amount, Department, and Effective Dates for maximum readability.

## References

1. *Richmond Civic Hackathon: Richmond's best hustlers, hackers, and artists solving the city's toughest challenges. - Devpost*. https://hack-for-rva.devpost.com/?ref_feature=challenge&ref_medium=discover
2. *https://data.richmondgov.com/resource/xqn7-jvv2.csv*. https://data.richmondgov.com/resource/xqn7-jvv2.csv
3. *City Contracts | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Well-Managed-Government/City-Contracts/xqn7-jvv2
4. *Hack for RVA a Civic Hackathon Happening in March - RVAHub*. https://rvahub.com/2026/02/17/hack-for-rva-a-civic-hackathon-happening-in-march/
5. *Contract Opportunities | SAM.gov*. https://sam.gov/opportunities
6. *eVA (Virginia's eProcurement Portal) - GovCon Glossary | Sweetspot*. https://www.sweetspot.so/glossary/eva-virginias-eprocurement-portal/