# RVA.gov Search and Structure Playbook: From Department Pages to Citizen Tasks

## Executive Summary

The City of Richmond's official website, RVA.gov, presents a classic challenge for civic technology: it is structured around the city's organizational chart rather than the tasks citizens actually need to perform. While the site features a modern Drupal-based architecture hosted on Acquia [1], its information architecture heavily favors department-first navigation, surfacing over 30 distinct departments in its primary menus [2] [3]. 

For a hackathon team building a unified search layer, the primary objective is to invert this model. By scraping decentralized content across multiple subdomains and applying custom relevance tuning for task-oriented verbs, you can create a "Virtual City Hall" experience that prioritizes citizen needs over bureaucratic boundaries. Note: the `business_unit` facet parameter is non-functional for programmatic JSON filtering (corrected 2026-03-18); it is visible in the Drupal UI but cannot filter API responses.

## What We’re Building — A citizen-task-first search over RVA.gov’s distributed ecosystem

Success for this project means unifying department content, external applications, and PDF forms into a single, relevance-tuned, citizen-friendly search interface. The goal is to abstract away the complexity of Richmond's multi-domain ecosystem so that a user searching for "pay water bill" or "adopt a dog" is immediately routed to the correct transactional endpoint, regardless of which department owns the service.

## Platform & Architecture Confirmation

The RVA.gov platform is built on a robust, enterprise-grade content management stack. The city contracted with Tech Dynamism, a technology consulting firm, to develop the site, utilizing Acquia's cloud-based web content management platform to ensure high capacity and speed [4] [1]. 

This architecture relies on Drupal 8+ and utilizes the Drupal Search API combined with the Facets module. Note: the `business_unit` facet parameter (`f[0]=business_unit:{id}`) is non-functional in the SODA API — JSON filtering via this parameter does not work (corrected 2026-03-18). It is visible in the Drupal search UI but cannot be used for programmatic JSON filtering.

## Information Architecture

RVA.gov's information architecture is fundamentally department-centric, with a light "services" overlay. The global navigation and "burger menu" prominently feature a massive list of city departments, ranging from Animal Care and Control to Public Utilities and Social Services [2] [3]. While the homepage does include a "Browse By Service" cue [2], the underlying structure requires users to understand which department handles their specific issue.

| Navigation Paradigm | Implementation on RVA.gov | Hackathon Strategy |
| :--- | :--- | :--- |
| **Primary Navigation** | 30+ Departments listed alphabetically in mega-menus [2]. | Demote department names in search relevance; use them strictly as filtering facets. |
| **Service Discovery** | Fragmented across department pages; some centralized "Virtual City Hall" links [1]. | Create a cross-department "Services" taxonomy aligned to top citizen tasks. |
| **External Routing** | Links out to specialized portals (e.g., apps.richmondgov.com for property search) [3]. | Index these external application URLs as high-priority "Task" entities. |

## Search Architecture

The native search runs on Drupal Search API with the Facets module, which natively supports filtering by business unit. However, native ranking is likely relevance-first based on keyword density, not citizen-task-first, and lacks turnkey support for local synonyms or typo tolerance.

| Search Capability | Native RVA.gov Implementation | Hackathon Augmentation |
| :--- | :--- | :--- |
| **Filtering** | URL-based facets (`f[0]=business_unit:{id}`). | Expose Department, Content Type, and Recency in the custom UI. |
| **Ranking** | Standard Drupal/Solr keyword relevance. | Boost "task verbs" (pay, apply, report); de-boost administrative pages. |
| **Synonyms & Typos** | Limited or requires heavy backend Solr tuning. | Implement app-side fuzzy matching and a local synonym dictionary (e.g., "trash" = "solid waste"). |

## Sitemap, Crawling, and Page Discovery

rva.gov/sitemap.xml returns 404 — the sitemap does not exist (corrected 2026-03-18). Teams must crawl manually using hub pages and search pagination as entry points.

| Discovery Method | Target URLs | Strategy |
| :--- | :--- | :--- |
| **Hub Crawling** | `/departments`, `/press-releases-and-announcements/news` [5]. | Extract all child links to map the department hierarchy and recent news. |
| **Search Pagination** | `/search?search=a&page={n}` | Iterate through search result pages to enumerate indexed content. |
| **Robots.txt** | `/robots.txt` | Check for official crawl directives; do not expect a sitemap reference. |

## Multi-Domain Content Integration

A true "city search" cannot be limited to the `www.rva.gov` domain. Critical citizen services and data are hosted across a fragmented ecosystem of subdomains and external agency sites [3].

| Domain / Subdomain | Content Type | Inclusion Strategy |
| :--- | :--- | :--- |
| **apps.richmondgov.com** | Property Search, Traffic Info, Fraud Hotline [3] [6]. | Index as high-priority transactional endpoints. |
| **data.richmondgov.com** | Open Data Portal [7]. | Index dataset titles and descriptions. |
| **rvalibrary.org** | Richmond Public Library [3]. | Include as a federated search source or distinct category. |
| **richmondvaannouncements.blogspot.com** | Legacy News Archive [5]. | Deprioritize; focus on current RVA.gov news feeds. |

## Department Facets Inventory

To build a functional filtering system, you can observe `business_unit` identifiers in the Drupal Facets UI. However, the `business_unit` facet parameter is non-functional for programmatic JSON filtering via the SODA API (corrected 2026-03-18). For content discovery, scrape the search results page HTML for anchor tags containing `f[0]=business_unit:` to build a mapping of internal IDs to human-readable department names — but use this mapping for UI display only, not for API filtering [3].

## Content Freshness & Governance

Content governance on RVA.gov is decentralized. According to the site's launch announcement, content managers for each department update their information in real time [1]. This leads to inconsistent freshness signals. While news items clearly display "Posted on" dates (e.g., "Posted on Aug 27, 2025") [8], many standard pages lack a "last updated" banner. 

To handle this, compute a heuristic "freshness score" by combining explicit dates, HTTP Last-Modified headers, and file path timestamps (e.g., PDF directories like `/sites/default/files/2026-01/`) [6].

## Translation & Language Access

RVA.gov utilizes a Google Translate widget and provides "En espanol" and "Language Access" entry points in its menus [3]. However, relying solely on machine translation for critical government services poses risks regarding accuracy and legal compliance (e.g., Title VI requirements). 

In your search layer, do not rely on automatic translation for critical services. Add disclaimers regarding machine translation limitations, and prioritize surfacing official, human-translated bilingual resources whenever they are available.

## Structured Data & Indexability

There is no obvious, site-wide implementation of `schema.org` or `application/ld+json` structured data on RVA.gov. Programmatic indexing will require custom heuristics. You must build your own lightweight schema in the index (defining entities like Department, Service, Form, News, and Event) derived from URL paths, breadcrumbs, and page headings.

## Hackathon Build Blueprint

To execute this search layer within a 48-72 hour hackathon, focus on the following pipeline:

1. **Data Pipeline:** Crawl hub pages and search pagination. Ingest PDFs (like the numerous permit applications found under Planning and Development Review) [6] with basic text extraction.
2. **Index Schema:** Define fields for `title`, `snippet`, `url`, `department`, `content_type`, `freshness_score`, and `domain`.
3. **Relevance Tuning:** Apply query-time boosts for task verbs (e.g., "pay", "apply") and implement recency decay for news items.
4. **UI/UX:** Build a clean interface featuring "Quick Actions" for the top 25 citizen tasks (e.g., paying taxes, applying for licenses) [1], alongside facets for department and content type.

## Risks, Limitations, and Workarounds

| Limitation | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **No Sitemap (returns 404)** | Incomplete content discovery. | Rely on search pagination scraping and hub-based crawling (corrected 2026-03-18). |
| **Fragmented Domains** | Users sent to unfamiliar URLs. | Clearly label external domains (e.g., "External Portal") in search results. |
| **Legacy Links** | Broken links or staging URLs (e.g., `rvagov.prod.acquia-sites.com`) [9]. | Implement automatic broken-link checks and canonicalize environment URLs during ingestion. |
| **Machine Translation** | Inaccurate translation of legal/service terms. | Display disclaimers; boost official Spanish-language pages. |

## Validation & Success Metrics

To prove the value of the new search layer, track the following KPIs during user testing:
* **Click-Through Rate (CTR) to Top Tasks:** Measure how quickly users find transactional pages compared to the native site.
* **Zero-Result Rate:** Monitor queries that return no results to identify missing synonyms or unindexed subdomains.
* **Time-to-Answer:** Track the reduction in time spent navigating department menus to find specific forms or services.

## Appendix

* **Key Hubs:** Homepage [2], Open Data [7], Forms [6], News [5].
* **Tech Stack Evidence:** Acquia and Tech Dynamism confirmation [4] [1].
* **Scripting Targets:** Target `https://www.rva.gov/search?search=a` to scrape HTML for `f[0]=business_unit:{id}` facet labels — for display mapping only; this parameter is non-functional for SODA JSON API filtering (corrected 2026-03-18).

## References

1. *City launches RVA.gov, new web platform to replace richmondgov.com | Richmond*. https://www.rva.gov/press-releases-and-announcements-mayors-office/news/city-launches-rvagov-new-web-platform-replace
2. *| Richmond*. https://www.rva.gov/
3. *Citizen Service and Response | Richmond*. https://www.rva.gov/citizen-service-and-response
4. *Tech Dynamism | Tech Agnostic Consultancy*. https://techdynamism.com/
5. *Press Releases and Announcements News | Richmond*. https://www.rva.gov/press-releases-and-announcements/news
6. *Forms | Richmond*. https://www.rva.gov/planning-development-review/forms
7. *Open Data Portal | Richmond*. https://www.rva.gov/information-technology/open-data-portal
8. *Event | RVA Builds: The Infrastructure Information Initiative | Richmond*. https://rva.gov/press-releases-and-announcements-public-works/news/event-rva-builds-infrastructure-information
9. *Special Event Planning | Richmond*. https://www.rva.gov/parks-recreation/special-event-planning