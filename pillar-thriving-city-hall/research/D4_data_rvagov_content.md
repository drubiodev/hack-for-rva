# Unlocking rva.gov for Service Navigation: Crawl, Structure, and API Reality Check

## Executive Summary

Building a service navigation tool on top of rva.gov requires a pragmatic approach to data extraction. The site operates as a traditional server-rendered Drupal application rather than a modern Single Page Application (SPA) with exposed JSON APIs. The most critical finding for your hackathon team is that the official Search UI is HTML-only, and no public JSON endpoint was observed during this inventory. 

However, the site possesses a highly structured, high-signal hub at `/common/services` that groups content into 11 distinct categories and embeds standardized department contact blocks. By using this hub as your primary crawl seed, you can reliably extract service-to-department relationships, bypass the opaque search relevance algorithm, and build your own structured index. You will need to account for off-domain service links (like EnerGov and OpenGov) and implement workarounds for Cloudflare-obfuscated email addresses.

## What’s Programmatically Available, Fast

You can reliably extract service categories, department contacts, and high-value links directly from server-rendered HTML. Because there is no confirmed JSON Search API, your team must plan to crawl and index the site manually. 

The Services hub (`/common/services`) is your highest-signal seed [1]. It acts as a curated directory rather than a raw list of pages. By scraping this single hub, you can immediately map the core ontology of the city's digital services without needing to spider the entire domain. The site renders complete HTML with consistent menus (such as the "RVA Burger Menu"), meaning you can use a lightweight, standard HTTP crawler without the overhead of a headless browser like Puppeteer or Playwright [2] [3].

## Crawlability & Discovery Plan

Confirming robots.txt and sitemap status is your first operational step. If sitemaps are absent or outdated, you must seed your crawler from the homepage and the Services hub, throttle your requests, and strictly cap your crawl depth.

Legacy paths are a known failure mode. For example, the path `/departments` currently returns a 404 error, indicating that the site's information architecture has drifted over time [4]. To avoid dead ends, never synthesize URLs based on assumptions; only follow live navigation links. 

Your discovery strategy should rely on the following global seeds:
* The homepage "Browse by Department" block [5].
* The "Browse the City of Richmond by services" hub at `/common/services` [5] [1].
* The press and announcements root for fresh content [5].

For the hackathon crawl envelope, configure your scraper to run at 0.5–1 requests per second with 2–4 concurrent threads. Obey `robots.txt` directives and identify your bot's user-agent with a contact email. Cap your crawl depth to 2, aiming for a maximum of 1,000 to 2,000 pages to ensure you finish indexing within the sprint.

## Information Architecture & Templates

Department contact blocks and service-category pages expose consistent fields that you can normalize immediately. However, there is no single, standardized "service description" content type; services are instead represented as curated links dispersed across departments and external systems.

The Services hub (`/common/services`) organizes links into 11 distinct top-level categories: Bills & Taxes, Employment, For Businesses, Legal, Permits & Planning, Public Safety, Recreation & education, Services & support, Transparency, Transportation, and Utilities [1]. 

Within these categories, the site embeds "Departments" sub-blocks with highly standardized fields. You can consistently extract the Department Name, Phone, FOIA contact, and Address [1]. 

### Handling Obfuscated Contact Data
A critical parsing challenge is that email addresses are frequently obfuscated by Cloudflare (appearing in the DOM as `[email protected]` with a `/cdn-cgi/l/email-protection` link) [1]. Your parsing strategy must either implement a Cloudflare email decoding script (using the `data-cfemail` attribute) or simply store the obfuscated mailto link as a fallback while surfacing the explicitly labeled FOIA contacts as reliable alternatives.

## Search Interface & Facets

The native Drupal search is HTML-only, features pagination, and enforces a minimum character limit. Facet IDs are not exposed in the URL structure, requiring reverse-engineering to build a programmatic filtering system.

When querying the search endpoint (e.g., `/search?search=water`), the system returns HTML results with pagination, displaying metrics like "Displaying 1 - 10 of 337" [6]. The search engine also enforces a strict query length, throwing an error message stating, "You must include at least one keyword to match in the content. Keywords must be at least 3 characters" if the input is too short [7]. 

While the UI implies faceted search capabilities (often using a `business_unit` taxonomy), the `business_unit` facet parameter is non-functional for SODA JSON API filtering (corrected 2026-03-18). It is visible in the Drupal search HTML but cannot be used to programmatically filter JSON API results. To extract the 40+ `business_unit` labels for display purposes only, inspect the DOM for `data-drupal-facet-item-value` attributes or view the page source for `drupalSettings.facetapi`. Build a custom dictionary mapping departments to slugs based on the homepage and Services hub listings for use as a display/navigation layer — not as an API filter.

## Structured Data & Schema.org

There is no evidence of JSON-LD or comprehensive Schema.org markup on the core service pages. You must compensate by defining and enriching your own internal schema.

The scraped content did not surface `GovernmentService` schemas, nor were departments annotated as `Organization` entities in a machine-readable format. Do not wait for official structured data. Instead, define your own internal schemas during ingestion:
* **Department**: name, phone, emails, FOIA, address, URL, business_unit_id.
* **Service**: title, category, owning_department, destination_url, internal/external flag.

Store provenance metadata (source_path, first_seen, last_seen) for every record to maintain trust and auditability.

## Content Freshness & Change Monitoring

News and press releases feature explicit dates, but evergreen service pages do not display visible "last updated" timestamps. You must combine feed detection with HTTP caching headers to monitor changes.

The homepage actively displays press releases and announcements with clear, explicit dates (e.g., "Mar. 16, 2026" and "Mar. 17, 2026") [5]. However, department and service pages lack these visible metadata markers. 

To monitor freshness without relying on search result recency, check the HTML `<head>` for `rel="alternate"` RSS or Atom feeds, and probe common Drupal feed paths (like `/rss.xml`). For service pages, track `ETag` or `Last-Modified` HTTP headers. If those are absent or inconsistent, fall back to computing a hash/checksum of the main content container to detect structural diffs.

## Available Structured Data Fields

You can capture consistent department contact fields and service-category relationships immediately using label-based extraction.

| Entity Type | Available Fields | Source Location | Extraction Method |
| :--- | :--- | :--- | :--- |
| **Department** | Name, Phone, Email (Obfuscated), FOIA Contact, Address | Homepage [5], `/common/services` [1] | Case-insensitive anchor matching ("Phone:", "FOIA:") |
| **Service Category** | Category Name (11 total), Service Link Title, Destination URL, External Flag | `/common/services` [1] | DOM parsing of category headers and nested lists |
| **Search Result** | Title, Snippet, URL, Submitted By, Date (if present) | `/search` [6] | DOM parsing of search result containers |
| **Staff Directory** | Name, Role, Programs, Phone, Email | `/housing-and-community-development/staff-directory` [8] | HTML Table extraction |

## Programmatic Endpoints and Status

Plan to crawl HTML as your primary ingestion method, but probe JSON endpoints opportunistically to see if backend APIs are left open.

| Endpoint / Area | Observed Status | Programmatic Access | Next Step for Hackathon |
| :--- | :--- | :--- | :--- |
| `/common/services` | Live; 11 categories; department blocks [1] | HTML scrape | Seed crawl; parse labels; map services to departments. |
| `/search?search=...` | Live; 3+ char min; 337 results for "water" [6] [7] | HTML scrape only; JSON not observed | Inspect view-source for `drupalSettings`; try `_format=json`. |
| `robots.txt` | Unconfirmed in this pass | Text fetch | Verify Disallow, Crawl-delay; note sitemap references. |
| `sitemap.xml` | Returns 404 — does not exist (corrected 2026-03-18) | Not applicable | Proceed directly with nav seeds; do not attempt sitemap-based discovery. |
| JSON:API (`/jsonapi`) | Unknown | HEAD/GET probe | If enabled, use `taxonomy_term` to list `business_unit` facets. |
| Department pages | Live; server-rendered [5] | HTML scrape | Extract contact fields; cap depth to 2. |

## Recommended Indexing Architecture for Hackathon

A focused HTML crawl combined with deterministic parsers and a pragmatic ranking model will deliver a credible navigation layer within a weekend sprint.

### Scope and Ingestion
Limit your seeds to `/common/services`, the homepage department list, and the press/announcements root. Cap your crawl depth at 2 (maximum 1,000–2,000 pages). Use a lightweight crawler that respects `robots.txt`. Build deterministic parsers that look for standard labels ("Phone:", "FOIA:") and normalize department slugs directly from the URL paths to deduplicate entities.

### Handling External Dependencies
The Services hub relies heavily on external systems. Critical tasks route users off-domain, such as the EnerGov online permit portal, OpenGov Procurement, ArcGIS Property Search, and Remit-Online for parking tickets [1]. Design your navigation layer to treat these off-domain destinations as first-class results. Maintain a whitelist of these external domains and flag them in your UI so users know they are leaving the main city site.

### Custom Relevance Ranking
Because the native Drupal relevance algorithm is opaque, implement a custom ranking model in your index. Apply heavy boosts for exact title matches, H1 tags, and URL path priority (favoring `/common/services` and department roots over deep pages). Apply recency boosts only to `PressItem` entities, ignoring dates for evergreen services unless a clear update signal is detected.

## Edge Cases & Failure Modes

Anticipate obfuscated data, legacy dead ends, and UI constraints that you should not inherit.

* **Cloudflare Obfuscation:** Emails are protected [1]. If you cannot decode them during the hackathon, store the `mailto` link and prioritize the FOIA contact.
* **Legacy Paths:** Paths like `/departments` return 404s [4]. Never guess URLs; only crawl what is linked.
* **Search Constraints:** The native search requires 3+ characters [7]. Your custom index should accept shorter queries (e.g., "IT", "HR") to provide a superior user experience.
* **PDF Traps:** Staff directories often exist as PDFs (e.g., August 2022, January 2025, March 2026) [9] [10] [11]. Exclude `.pdf` from your primary HTML crawl to avoid polluting your search index with unstructured text, unless you specifically implement a PDF parsing pipeline.

## Validation & Measurement

Prove your index works by using task-oriented tests and spot-checking extracted fields for correctness.

Run relevance tests using 10 to 15 common citizen tasks (e.g., "water", "permits", "trash collection", "pay bill", "jury duty"). Measure success by whether the top 3 results include the expected service or department link. Conduct a field accuracy audit for 25 random departments to ensure phone numbers, FOIA contacts, and addresses mapped correctly. Finally, establish a 50-URL control set to re-crawl weekly, alerting your team to any structural DOM changes.

## Open Questions & Next Actions

A short 48-hour probe cycle will de-risk unknowns before your coding sprints begin.

Your technical lead should immediately fetch `robots.txt` on `rva.gov` and `www.rva.gov` to archive the results. Note: `sitemap.xml` returns 404 on rva.gov — it does not exist (corrected 2026-03-18); do not rely on it. Concurrently, execute HEAD/GET requests against `/jsonapi` and `/search?_format=json` to definitively rule out hidden JSON endpoints. If JSON:API is enabled, export the `business_unit` terms. Meanwhile, the engineering team should begin setting up the lightweight crawler and label-based parsers based on the `/common/services` HTML structure.

## References

1. *Services | Richmond*. https://rva.gov/common/services
2. *404 Page Not Found | Richmond*. https://rva.gov/parks-recreation-community-facilities
3. *Planning & Development Review | Richmond*. https://rva.gov/planning-development-review
4. *404 Page Not Found | Richmond*. https://rva.gov/departments
5. *| Richmond*. https://www.rva.gov/
6. *Search | Richmond*. https://www.rva.gov/search?search=water
7. *Search | Richmond*. https://www.rva.gov/search?search=a
8. *Staff Directory | Richmond*. https://www.rva.gov/housing-and-community-development/staff-directory
9. *Directory*. https://www.rva.gov/sites/default/files/2022-08/P%20%26%20I%20Directory%20-%20August%202022_0.pdf
10. *PDR Website Staff Contact Directory*. https://www.rva.gov/sites/default/files/2025-01/PDR%20Website%20Staff%20Contact%20Directory%20-%20January%202025_0.pdf
11. *Directory*. https://rva.gov/sites/default/files/2026-03/Website%20Directory%20Page%20-%20%20March%202026.pdf