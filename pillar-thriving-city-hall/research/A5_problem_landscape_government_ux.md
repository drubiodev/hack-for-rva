# Fixing Findability: Turning RVA.gov’s Search and Navigation into a Resident-Centered Service Finder

## Executive Summary

Government websites frequently fail residents not because the information is missing, but because the information architecture (IA) mirrors internal organizational charts rather than user tasks. Nearly 70% of citizens report frustration when trying to complete basic tasks on government websites, with poor navigation cited as the primary obstacle [1]. On Richmond's RVA.gov, a simple query for "property search" returns 409 results, highlighting a high-noise environment where service tasks get buried [2]. 

This findability crisis drives residents away from digital self-service and toward expensive support channels like call centers and in-person visits. Furthermore, research demonstrates that technical accessibility compliance does not guarantee usability; screen reader users often struggle to navigate government sites that lack clear structural wayfinding [3]. 

To resolve these issues, municipalities must adopt a "services-first" taxonomy, implement plain-language standards mandated by the Plain Writing Act of 2010 [4], and optimize faceted search interfaces for mobile users [5]. With the City of Richmond currently fielding its 2026 Community Survey to 4,000 households [6], there is an immediate strategic window to establish baseline metrics for digital satisfaction and prototype high-impact UX improvements.

## Problem Landscape — Residents can’t find services because content and IA mirror the org chart, not user tasks

Government agencies and universities share a structural problem: their websites are organized around how the institution is organized, rather than what users are trying to do [7]. This structural failure to surface critical information has real operational costs, driving residents to call, email, or walk in to ask questions that are already answered online [7].

### Evidence of result noise on RVA.gov — 409 results for a common task

When users cannot find what they need in the navigation, they turn to search. However, on many public-sector sites, search results are little more than keyword matches across thousands of pages [7]. On RVA.gov, a basic search for "property search" yields 409 results [2]. *Inference: This high volume of results for a highly specific, common task indicates that the search engine prioritizes quantity over quality, burying the actual service application beneath press releases, meeting minutes, or unrelated departmental pages.*

### Why org-chart IAs fail residents — task vs. department mismatch

A resident looking to register a vehicle or apply for a permit should not need to know which specific city department handles that jurisdiction [7]. When navigation mirrors bureaucratic org charts, it creates a cognitive burden that defeats the purpose of digital self-service [1]. The fix requires accepting that the website exists to serve the public and building navigation around their tasks, not internal organizational structures [7].

## National Patterns of Resident Search Behavior — People use task language; keyword-only search returns the wrong content types

Residents search for "what to do" using plain language. When government websites rely on traditional keyword matching, users who type "food assistance" often get a press release mentioning the program instead of the page that actually explains how to apply [7]. 

### Failure Modes Comparison

The following table outlines the four most common failure modes in government website navigation and search:

| Failure mode | What’s really happening | Evidence | Impact | What now |
|---|---|---|---|---|
| Department-centric nav | Users must know org names to find tasks | Government websites tend to be organized around institutional structure [7]. | Abandonment, increased call volume | Adopt a services-first taxonomy grouped by citizen intent [1]. |
| Wrong/insider terms | Jargon blocks queries | Content is easier to understand when using language made for the specific audience [8]. | Low search success | Rewrite labels using plain language [4]. |
| Result-type noise | Press/news outrank service pages | Keyword matching returns press releases instead of application pages [7]. | Missed tasks, 409-result noise [2] | Boost service pages, implement "best bets" |
| Mobile/filter UX gaps | Filters hidden; sort ≠ filter | Sorting is for reordering; filtering is for narrowing down [5]. | Low mobile self-service | Inline filters, distinct from sorting [5]. |

*Takeaway: These recurring failure modes require a holistic approach that aligns information architecture, content strategy, and search engine tuning.*

### Risk/Opportunity Snapshot — “Fix content before search”

When findability becomes a visible problem, the instinct is often to replace the search tool [7]. However, putting a new AI-powered search tool on top of badly organized or poorly written content will simply return the same bad results faster [7]. Agencies must conduct thorough audits, reorganize navigation around user tasks, and establish governance before investing in technical search improvements [7].

## Accessibility and Digital Literacy Barriers — Accessible code without wayfinding still fails real users

Government websites must serve every demographic simultaneously, making accessibility non-negotiable [1]. However, technical compliance with standards like WCAG does not automatically equate to a usable experience for residents with disabilities.

### Screen reader and orientation pitfalls

Research evaluating e-government websites reveals that a website can be rated highly for accessibility while still failing usability tests [3]. For example, screen readers may read through a page without clearly providing the user any information about the structure or hierarchy of the website [3]. Without proper navigation schemes to show users where they are in the context of the site's hierarchy, it is often impossible for blind users to complete a task or perform a search request [3].

### Facets and chips for comprehensibility

Faceted search allows users to filter results by attributes [9]. To make this accessible and comprehensible, the VA.gov Design System provides strict guidance: if a product's main purpose is to allow users to search, it should use a persistent, visible, left-side navigation for filters on tablet and wider viewports [5]. Furthermore, if there are more than 3 facets applied, the interface must use filter chips to clearly show users what is currently selected [5]. Filtering must happen inline on the page without taking users to a new screen [5].

## Richmond Context — Evidence, gaps, and an immediate measurement window

RVA.gov utilizes a faceted search approach, but public evidence suggests there is room for significant optimization to meet modern digital service standards.

### What’s publicly visible on rva.gov search

The RVA.gov search results page prominently features tabs for both "Site Search" and "Google Search" [2]. *Inference: Exposing a Google Search fallback directly on the results page is a common indicator that the internal site search frequently underperforms, forcing users to rely on external engines to navigate the city's domain.* Coupled with the 409 results returned for a simple "property search" [2], this implies significant tuning gaps in the search index.

### Community Survey timing and reporting

The City of Richmond recently announced the mailing of the 2026 Richmond Community Survey to 4,000 randomly selected households [6]. This survey measures public opinion on community livability and satisfaction with City services [6]. Results will be published on the City Auditor’s webpage [6] [10]. *Inference: While the Auditor's page lists dozens of reports on city operations [11], there is a historical gap in public metrics specifically regarding website usability and search satisfaction. The current survey window presents an ideal time to align website KPIs with broader city service satisfaction metrics.*

### Content risks: PDFs and legacy documents

Critical service instructions on RVA.gov are sometimes trapped in legacy formats. For example, the "City Of Richmond Online Permit Portal User Guide" is hosted as a PDF from 2019 [12]. Unstructured PDFs hurt search relevance, are notoriously mobile-unfriendly, and create dead ends for users trying to complete digital tasks.

## Drupal + Faceted Search Realities — Strengths, common pitfalls, and low-lift improvements

Drupal-based government sites commonly use Search API with Facets. While powerful, this configuration requires deliberate UX design to serve citizens effectively.

### What good looks like (grounded in VA DS patterns)

Effective faceted search implementations do not conflate the "Sort" action with the "Filter" action [5]. Good implementations provide a persistent left-hand sidebar for filtering, keep filtering inline without page reloads, and utilize filter chips to summarize active selections when users apply multiple constraints [5]. 

### Common pitfalls and how to mitigate now

Without proper configuration, faceted search devolves into keyword chaos. Common pitfalls include over-indexing press releases, using internal bureaucratic jargon for facet labels, and hiding filters on mobile devices. These can be mitigated by tuning the search index to boost service-oriented content types, demoting news articles, and rewriting facet labels in plain language.

## Plain-Language Content Strategy — Translate bureaucracy into resident verbs and outcomes

Plain language is not just a best practice; it is the law. The Plain Writing Act of 2010 requires federal agencies to write clear government communication that the public can understand and use [4] [13]. 

### Write and test for understanding

Plain language writing requires communicating clearly for a specific audience [8]. Content strategists must focus on what users want to know and address separate audiences separately [14]. *Inference: Replacing internal jargon (e.g., "PDR" or "permitting") with resident-friendly verbs (e.g., "build a deck") directly improves search match quality and reduces misroutes to 311.*

### Governance and checklists

To maintain plain language standards, organizations should utilize established resources like the checklists provided by PlainLanguage.gov and Digital.gov [15] [16]. Establishing a content style guide specifically for navigation labels—specifying maximum character counts and prohibiting bureaucratic terms—prevents the gradual accumulation of navigation debt [1].

## Measurement & Governance — Preventing navigation debt and proving ROI

Technical solutions fail without organizational processes to maintain them [1]. 

### KPIs and feedback loops

Government websites need comprehensive analytics tracking menu usage, search success rates, and task completion flows [1]. Creating a navigation performance dashboard that tracks metrics like time-to-task and support call reduction allows for evidence-based iteration rather than redesigns based on internal opinions [1].

### Governance mechanics

Agencies must create a navigation governance committee with representatives from IT, communications, and key departments [1]. This committee should enforce clear rules: no department can add top-level navigation items without approval, and all new content must fit within a services-first taxonomy [1].

## Hackathon: 3 Prototypes with outsized impact in 48–72 hours

For a hackathon team looking to prototype immediate UX improvements for RVA.gov, the following three initiatives offer the highest ROI:

| Prototype | Problem it solves | What to build this weekend | Success metric |
|---|---|---|---|
| **Service Search "Best Bets" + Boosting** | Press/news outrank services; 409-result noise [2] [7]. | Add curated top results for the top 20 tasks; boost service content types; demote news/press; add a synonyms dictionary. | +20–30% click-through to correct service pages; lower pogo-sticking. |
| **Resident-Language Facets + Filter Chips** | Insider labels confuse users; filters are hidden or conflated with sorting [5]. | Rename facets to action verbs ("Apply," "Pay"); implement inline filter chips for 3+ active filters [5]; separate filter from sort. | +25% filter usage; shorter time-to-result. |
| **311 Category Mapper** | Category confusion and misroutes to 311 support. | Build a plain-language intake form that maps resident terms (e.g., "pothole") to official 311 bureaucratic categories. | -15% 311 misroutes; higher self-serve completion. |

*Takeaway: These prototypes focus on thin-slice wins that compound over time: better ranking, clearer labels, and guided handoffs.*

## Unknowns

Based on publicly available data, the following elements cannot be verified:
* There are no publicly available, recent metrics on resident satisfaction specifically regarding RVA.gov site search or navigation (the City Auditor’s reports page lists no such specific digital usability studies) [11].
* There is no published analysis of RVA.gov 311 category confusion or misroute rates located in public sources.
* There is no official public documentation detailing RVA.gov’s specific Drupal Search API/Solr configuration, ranking rules, synonym dictionaries, or facet taxonomy.

## References

1. *How to Improve Website Navigation for Government Services*. https://optasy.com/blog/how-improve-website-navigation-government-services
2. *Search | Richmond*. https://www.rva.gov/search?search=property%20search&page=0
3. *the-usability-and-content-accessibility-of-the-e-government ...*. https://scispace.com/pdf/the-usability-and-content-accessibility-of-the-e-government-syzr6wo4ik.pdf
4. *Plain Language Guide Series - Digital.gov*. https://digital.gov/guides/plain-language
5. *Search results - VA.gov Design System *. https://design.va.gov/templates/search-results
6. *City of Richmond Announces Mailing of 2026 Richmond Community Survey to Residents | Richmond*. https://www.rva.gov/citizen-service-and-response-office-city-auditor-press-releases-and-announcements/news/city
7. *Why Users Can’t Find Information on Government and Higher Ed Websites*. https://electriccitizen.com/resources/why-users-cant-find-information-government-higher-ed-websites
8. *Writing for understanding - Digital.gov*. https://digital.gov/guides/plain-language/writing
9. *Search Filter - VA.gov Design System *. https://design.va.gov/components/search-filter
10. *Richmond seeks public feedback on quality of life, services with 2026 Community Survey | WRIC ABC 8News*. https://www.wric.com/news/local-news/richmond/2026-community-survey-mailed-out/
11. *Reports Issued | Richmond*. https://www.rva.gov/office-city-auditor/reports-issued
12. *City Of Richmond Online Permit Portal User Guide*. https://www.rva.gov/sites/default/files/2019-12/OPP%20User%20Guide.pdf
13. *Plain language | GSA*. https://www.gsa.gov/governmentwide-initiatives/plain-language
14. *Write for the reader - Digital.gov*. https://digital.gov/guides/plain-language/principles/write-for-reader
15. *Plain Language Web Writing Tips*. http://digitalgovernmenthub.org/library/plain-language-web-writing-tips/
16. *Plain Language | Office of Information Technology*. https://oit.colorado.gov/standards-policies-guides/guide-to-accessible-web-services/plain-language