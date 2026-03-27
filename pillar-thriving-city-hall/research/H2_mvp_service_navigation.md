
# RVA Resident Service Navigator MVP: Fastest, Safe Path to a Judge-Ready Demo in 48 Hours

## Executive Summary

To deliver a winning, compliant prototype within a 48-hour window, the team must prioritize reliability over breadth. Given the constraint of no post-2018 RVA311 API, building a hardcoded **Decision Tree (Approach A)** is the safest and most effective strategy. It guarantees a flawless demo for the most common resident scenarios while strictly adhering to the rules against simulating official submissions. 

Key insights driving this recommendation:
* **Current web data beats legacy datasets:** The 2014 to 2015 Socrata datasets are too outdated for accurate routing [1] [2]. Instead, the taxonomy must be built from current rva.gov service pages, which explicitly list fees, schedules, and rules [3] [4].
* **Disambiguation is critical:** Services like graffiti removal and storm debris require context to route correctly (e.g., DPW vs. Police) [3] [5]. A decision tree handles this elegantly.
* **Human fallback is mandatory:** Every path must prominently display the official 3-1-1 and 804-646-7000 phone numbers to ensure compliance and user trust [6] [7].

## Problem and constraints recap

The core challenge is to build a helpful, mobile-friendly resident service navigator without access to the modern RVA311 API. The solution must guide residents to the correct category or link, provide a human fallback, and strictly avoid any claim of official City authority or simulation of actual service submissions. With over 50 request types across 7 department groups [6], attempting full coverage in 48 hours is a massive risk. Success depends on scoping the problem to the most impactful scenarios and delivering a polished, reliable mobile experience.

## Ground-truth data landscape

Relying on the 2014 to 2015 Socrata open data portal [1] [2] introduces significant risk of outdated information. Instead, the current rva.gov website provides authoritative, high-signal data for building the taxonomy. The "About RVA311" page outlines the primary partner groups, including Public Works, Public Utilities, Social Services, Finance and Revenue, and Planning and Development [6]. 

Crucially, individual service pages contain the exact operational rules needed for the MVP:
* **Bulk and Brush:** Bi-weekly collection mirroring recycling; $100 fee for 24-hour requests; $50 fee for appliance collection [8] [3].
* **Leaf Collection:** Vacuum service requires a $30 fee payable via RVA311 or mail [4].
* **Graffiti:** DPW handles public right-of-way; private property requires a consent form; known suspects should be reported to Police at 804-646-5100 [5].

## Top resident needs to cover first

To maximize impact, the MVP should focus on 20-30 categories that solve the majority of resident traffic, heavily weighting Department of Public Works (DPW) and Department of Public Utilities (DPU) operational services. 

The initial category list should include:
* **Trash & Debris:** Missed pickup, Bulk/Brush, Yard Waste, Leaf Vacuum ($30), Appliance Pickup ($50) [8] [3] [4].
* **Infrastructure:** Potholes, Streetlight Out, Sidewalk Maintenance, Street Cleaning, Snow Removal [9].
* **Neighborhood:** Graffiti (public vs. private), Code Enforcement, Animal Control [6] [5].
* **Utilities & Finance:** Water leaks, billing, Taxes, Business Licensing [6].

## Approach comparison

The following table evaluates the three proposed approaches against the 48-hour constraint.

| Dimension | A) Minimum Decision Tree | B) Search-Based Helper | C) Hybrid (Tree + Search) |
|---|---|---|---|
| **Build time** | 8-12 hours | 12-16 hours | 16-20 hours (risky in 48h) |
| **Data needed** | JSON for 20-30 categories; 5-8 Q logic; 50-60 official links/phones | 50-100 curated rva.gov pages; keyword/synonym list (100-200 terms) | Union of A + minimal B (30-40 pages indexed) |
| **Coverage** | 20-30 categories; 5 scripted scenarios flawless | Broader discovery via NL queries; top-3 ranked suggestions | Best of both; tree for known, search for unknown |
| **Failure modes** | Uncovered intents; over-simplified branching | Misranking; ambiguous queries; index drift; noisy pages | Integration complexity; QA time blowout |
| **Fallback** | Always present 3-1-1 / 804-646-7000; RVA311 link | Same; also show top category CTAs | Same |
| **Compliance risk** | Low (no simulation; clear disclaimers) | Medium (ranking can imply authority if phrased poorly) | Medium-High (coordination/consistency) |
| **Judge demo strength** | High (5 clean journeys) | Medium (depends on ranking quality) | Medium-High if finished; risky if partial |

Approach A is the clear winner for a hackathon environment, offering the highest reliability and lowest compliance risk.

## Approach A feasibility

**Feasibility:** Highly feasible within 8-12 hours.
This approach relies on a curated JSON dataset mapping 5-8 questions to 20-30 categories. The minimum dataset requires defining the 7 department groups [6], 50-60 official links, and persistent phone fallbacks (3-1-1 and 804-646-7000) [7]. It also requires disambiguation prompts for tricky categories (e.g., "Is the downed limb an emergency?"). 

The primary failure mode is uncovered intents, which is mitigated by a robust "catch-all" fallback directing users to call 311. A "good enough" demo consists of 5 scripted scenarios (e.g., missed trash, pothole, graffiti) that flawlessly guide the user to the correct official link and payment note, ending with a clear call-to-action.

## Approach B feasibility

**Feasibility:** Doable in 12-16 hours, but carries higher risk.
This approach requires crawling 50-100 curated rva.gov pages and building a keyword/synonym index mapped to 30-40 categories. The minimum dataset relies heavily on tuning synonyms (e.g., "trash can," "bin," "cart"). 

The main failure modes are misranking ambiguous queries and returning 404s or irrelevant press pages. If the top suggestion is wrong, user trust evaporates. A successful demo would show a natural language query (e.g., "My trash wasn't picked up") returning the "Missed Trash Pickup" category with a direct link and explanation.

## Approach C feasibility

**Feasibility:** Too risky for a 48-hour window unless Approach A is finished extremely early.
This hybrid model offers the best user experience but introduces significant integration complexity and QA overhead. The minimum dataset is the union of A and B. The primary failure mode is inconsistent routing between the tree and the search fallback. A demo would need to showcase both structured paths and search fallbacks seamlessly.

## Taxonomy and content sourcing plan

The taxonomy must be derived directly from current rva.gov service pages to ensure accuracy regarding rules and fees. 

Key data points to embed in the JSON logic:
* **Bulk & Brush:** Note the bi-weekly schedule, prohibited items (construction debris, paint), and the $100 24-hour option [3].
* **Leaf Collection:** Explicitly state the $30 vacuum fee and direct users to RVA311 for payment [4].
* **Graffiti:** Differentiate between public property (DPW handles) and private property (requires consent form). Note the 804-646-5100 police number if a suspect is known [5].
* **Trash Collection:** Provide transfer station hours and note the $50 appliance pickup fee [8].

## Compliance, trust, and human fallback

To satisfy the constraints, the MVP must never appear as an official submission portal. 
* **UI Copy:** Prominently display: "This is an independent helper. Not an official City of Richmond service. Do not submit confidential info here."
* **Persistent Fallback:** Every screen must show: "Call 3-1-1 or 804-646-7000 or visit rva311.com to submit requests/pay fees" [6] [7].

## Recommended MVP

**Recommendation: Approach A (Minimum Decision Tree)**
Build the decision tree to 100% completion. Only attempt a tightly-scoped version of Approach B (micro-search over 30-40 pages) if Approach A is fully stable and QA'd by hour 18. 

The minimum viable feature set includes a mobile-first UI, 5-8 routing questions, 25-30 mapped categories, disambiguation for complex issues, and persistent fallback CTAs.

## Go/no-go criteria

The team should only proceed to the demo if the following criteria are met:
* 25+ categories are accurately mapped to authoritative rva.gov/RVA311 links.
* 5 scripted scenarios pass end-to-end without errors.
* Disclaimers and 3-1-1/804-646-7000 fallbacks render correctly on mobile devices.
* Unknown intents successfully route to the "call 311" fallback.
* All links are validated (no 404s) on the morning of the demo.

## Demo script and success metrics

The demo should prove value in under 3 minutes by executing five flawless journeys:
1. Missed trash pickup
2. Bulk/Brush timing and rules
3. Pothole reporting
4. Streetlight out
5. Graffiti on private property

**Success metrics:** 100% correct final links, fewer than 3 taps to reach an answer, 100% visibility of fallback CTAs, and zero claims of official authority.

## Build plan for 48 hours

* **Hours 0-4:** Curate 25-30 categories and links from rva.gov; write disambiguation prompts.
* **Hours 4-8:** Implement responsive tree UI, JSON wiring, and disclaimers.
* **Hours 8-12:** QA the 5 core scenarios; refine copy.
* **Hours 12-18:** Expand to 30 categories; validate all links; polish mobile CSS.
* **Hours 18-24 (Optional):** Implement micro-search if time permits.
* **Final:** Dry-run demo, final link check, and capture backup screenshots.

## Risks and mitigations

* **Risk:** Misrouting users due to ambiguous categories.
 * **Mitigation:** Use clarifying questions (e.g., "Is it on public or private property?") before providing a link.
* **Risk:** Content drift (fees or links change).
 * **Mitigation:** Run a link validation script before the demo; rely only on official rva.gov pages.
* **Risk:** Schedule overrun.
 * **Mitigation:** Strictly time-box the build. Defer any search functionality until the core decision tree is perfect.

## Post-demo enhancements

Following a successful hackathon demo, the prototype can be expanded into a production-grade tool by broadening category coverage, integrating a full search index with nightly link checks, adding localized language support, and conducting a full WCAG 2.1 AA accessibility review.

## References

1. *Enterprise Zones | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/Economic-Growth/Enterprise-Zones/4isz-qcfi
2. *https://data.richmondgov.com/api/views/xqn7-jvv2/r...*. https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD&bom=true&format=true
3. *Bulk and Brush | Richmond*. https://www.rva.gov/public-works/bulk-and-brush
4. *Leaf Collection | Richmond*. https://www.rva.gov/public-works/leaf-collection
5. *Graffiti Removal | Richmond*. https://www.rva.gov/public-works/graffiti-removal
6. *About RVA 311 | Richmond*. https://www.rva.gov/citizen-service-and-response/about-rva-311
7. *RVA 311 Helpful Links | Richmond*. https://www.rva.gov/citizen-service-and-response/rva-311-helpful-links
8. *Trash Collection | Richmond*. https://www.rva.gov/public-works/trash-collection
9. *Neighborhood_Cleanups | Richmond*. https://www.rva.gov/public-works/neighborhoodcleanups