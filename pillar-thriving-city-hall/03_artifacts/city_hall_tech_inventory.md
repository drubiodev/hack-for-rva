# City Hall Tech Inventory — Richmond Systems Landscape

This document describes the technical systems that underpin Richmond City Hall operations, including programmatic access points and constraints relevant to hackathon builders.

All information here is based on publicly available sources and the rubric document. Teams should verify system status and access constraints before building against any of these systems.

---

## Resident-Facing Systems

### rva.gov — City Website
- **Platform:** Drupal 8+ (Drupal CMS)
- **Hosting:** Acquia (managed Drupal cloud)
- **Developer:** Tech Dynamism (contracted)
- **Search:** Drupal Search API with Facets module
- **Search URL pattern:** `https://www.rva.gov/search?search={query}&page={n}&f[0]=business_unit:{id}`
- **Department facets:** Over 40 department slugs visible in UI; `business_unit` facet parameter is non-functional in SODA API — JSON filtering via this parameter does not work (corrected 2026-03-18)
- **Translation:** Google Translate widget — 36 languages supported
- **Sitemap:** rva.gov/sitemap.xml returns 404 — does not exist; teams must crawl manually (corrected 2026-03-18)
- **Structured data:** No confirmed public JSON or XML export of service descriptions
- **Hackathon access:** Public web crawling and HTTP GET to search API are the primary access patterns
- **Constraints:** Not an official data API; crawled content may be stale; no authentication required for read access

### RVA311 — Service Request Platform
- **Platform:** AvePoint Citizen Services
- **Infrastructure:** Microsoft Dynamics 365 + Azure
- **Launch date:** June 15, 2018 (replaced SeeClickFix)
- **Request volume (2024):** ~203,000 calls and ~75,200 requests created (corrected 2026-03-18; prior figure of 208,216 was incorrect)
- **Request types:** ~50+ types across 7 department groups
- **Channels:** Web portal, mobile app, phone (311)
- **Public API:** None — AvePoint Citizen Services does not expose a public API
- **Open data:** No post-2018 data published to Socrata or any public endpoint
- **Historical data only:** SeeClickFix era data (Jan 2014–Aug 2015) on Socrata (vgg4-hjn8)
- **Hackathon access:** No programmatic access to live data; historical Socrata data only
- **Constraints:** This is the single largest data constraint for the resident service navigation problem

---

## Integration Middleware

### Microsoft BizTalk
- **Role:** Integration middleware connecting RVA311 (Dynamics 365) to downstream work order systems
- **Data flow:** Citizen request → RVA311 → BizTalk → Trimble Cityworks (DPW work orders)
- **Hackathon access:** No public access
- **Notes:** Understanding this integration explains why RVA311 data doesn't flow easily to open data portals

---

## Work Order & Permitting Systems

### Trimble Cityworks
- **Role:** DPW (Department of Public Works) work order management system
- **Integration:** Receives work orders routed from RVA311 via BizTalk
- **Hackathon access:** No public access
- **Notes:** Work order status is not publicly accessible; residents cannot query Cityworks directly

### EnerGov (Tyler Technologies)
- **Role:** Permitting, licensing, and code enforcement platform
- **Coverage:** Building permits, business licenses, zoning applications, code violations
- **Hackathon access:** Some permit data may be available via open data portal; direct API access not confirmed
- **Notes:** Tyler Technologies offers a public inquiry portal in some deployments; Richmond's configuration needs verification

### Oracle RAPIDS
- **Role:** Financial and procurement management system
- **Coverage:** Purchasing, contracts, accounts payable, budget
- **Hackathon access:** No public access; internal staff system
- **Notes:** Source of truth for City contracts; the public-facing representation is the Socrata dataset (xqn7-jvv2)

---

## GIS and Mapping

### ArcGIS (Esri)
- **Role:** City GIS platform for geographic data, service areas, and mapping
- **Data types:** Neighborhood boundaries, City council districts, service area polygons, infrastructure layers
- **Hackathon access:** ArcGIS REST API is publicly accessible for many City layers; specific layer IDs need verification
- **URL:** Richmond Open Data and ArcGIS Online (specific endpoint needs verification)
- **Notes:** Useful for geographic context in 311 routing tools (e.g., which council district is this address in?)

---

## Procurement Systems

### OpenGov
- **Role:** Used by some Virginia localities for procurement and budget transparency
- **Richmond use:** Prior Richmond procurement portal used a related OpenGov tool; current status needs verification
- **Hackathon access:** OpenGov provides a public procurement portal in some deployments

### City Contracts Open Data (Socrata)
- **Role:** Public-facing representation of the City contracts registry
- **Dataset ID:** xqn7-jvv2
- **API URL:** `https://data.richmondgov.com/resource/xqn7-jvv2.json` (returns all 9 columns correctly; corrected 2026-03-18 — prior "8-column bug" claim was incorrect)
- **CSV URL:** `https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD` (all 9 columns)
- **Hackathon access:** Fully public; no authentication required
- **Notes:** Both the API and CSV download return all 9 columns; no workaround needed

---

## Communication & Notification Infrastructure

### Microsoft 365 / Exchange
- **Role:** Staff email and communication
- **Hackathon access:** No public access

### Notify.gov / GovDelivery
- **Role:** Resident notification systems for alerts and service updates
- **Hackathon access:** No direct access for hackathon tools; outbound notification capability is City-controlled

---

## Summary: What Hackathon Teams Can Access

| System | Public Access | Notes |
|--------|--------------|-------|
| rva.gov | Yes (web crawl, search API) | No official data export |
| RVA311 live data | No | AvePoint has no public API |
| RVA311 historical (pre-2018) | Yes (Socrata vgg4-hjn8) | SeeClickFix era only |
| City Contracts (Socrata) | Yes (API + CSV download) | All 9 columns available via both API and CSV (corrected 2026-03-18) |
| ArcGIS City layers | Partially | Specific layer IDs need verification |
| SAM.gov | Yes (free API key) | Key registration required |
| eVA procurement | Yes (CSV on data.virginia.gov) | URL needs verification |
| VITA contracts | Yes (web only) | No API |
| USASpending.gov | Yes (no key needed) | Federal spending data |
| Oracle RAPIDS | No | Internal staff system |
| BizTalk / Cityworks | No | Internal middleware/work orders |
| EnerGov | Partially | Some permit data may be public |
