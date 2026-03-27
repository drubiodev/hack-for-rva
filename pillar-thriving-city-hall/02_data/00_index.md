# Data Index — A Thriving City Hall

This index summarizes the key datasets and data sources available for this pillar. Always verify access and schema before building.

---

## Resident Service Navigation Data

### RVA311 Historical Socrata Dataset (vgg4-hjn8)
- **What it is:** SeeClickFix-era 311 requests from Richmond (January 2014 – August 2015 only)
- **URL:** `https://data.richmondgov.com/resource/vgg4-hjn8.json`
- **Format:** SODA REST API, JSON, CSV
- **Columns include:** request type, status, address, neighborhood, date opened/closed
- **Critical limitation:** This data is from the SeeClickFix platform era. The current AvePoint Citizen Services platform (launched June 2018) has NO public API and does NOT publish to Socrata.
- **Use for:** understanding historical request categories and patterns; NOT representative of current volumes
- **Verified:** Yes (Socrata dataset exists and is queryable)

### rva.gov Drupal Search API
- **What it is:** Drupal Search API with Facets module on rva.gov (Drupal 8+, hosted on Acquia)
- **URL pattern:** `https://www.rva.gov/search?search={query}&page={n}&f[0]=business_unit:{id}`
- **Format:** HTML (no JSON API confirmed for external use)
- **Department slugs:** Over 40 known department slugs accessible via facet parameter
- **Translation:** Google Translate widget (36 languages supported)
- **Use for:** scraping and indexing City service information; building a search layer over public content
- **Verification needed:** rva.gov sitemap availability; structured data fields; current department slug list

### ArcGIS Richmond Layers
- **What it is:** City GIS layers for neighborhoods, districts, service areas
- **URL:** `https://www.arcgis.com/apps/` (Richmond-specific layers)
- **Format:** REST API, GeoJSON
- **Use for:** mapping service areas to neighborhoods; geographic context for 311 requests
- **Verification needed:** specific layer IDs and access method

---

## Procurement Data

### City Contracts Socrata (xqn7-jvv2)
- **What it is:** Richmond City contracts registry, records from ~January 2011 onward
- **API URL:** `https://data.richmondgov.com/resource/xqn7-jvv2.json`
- **CSV URL:** `https://data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD`
- **Format:** SODA REST API (8 columns only — known bug), CSV (all 9 columns)
- **Known bug:** The SODA API omits one column. Use the CSV download for complete data.
- **Columns include:** vendor name, contract amount, start date, end date, department, contract type
- **Use for:** contract expiry tracking, vendor analysis, spending transparency
- **Verified:** Dataset exists; column bug noted in rubric doc

### SAM.gov API
- **What it is:** Federal System for Award Management — federal contracts, awards, debarment
- **URL:** `https://sam.gov/` and `https://api.sam.gov/`
- **Format:** REST API (free API key required)
- **Use for:** federal contract data, vendor debarment checks, cross-source contract comparison
- **Verification needed:** current API key registration process and rate limits

### eVA (Virginia Electronic Procurement)
- **What it is:** Virginia statewide procurement data
- **URL:** `https://data.virginia.gov/` (search for eVA procurement CSV)
- **Format:** CSV download
- **Use for:** state-level contract comparison, VITA contract context
- **Verification needed:** current dataset URL and column schema

### VITA Statewide Contracts
- **What it is:** Virginia IT Agency statewide contract listing
- **URL:** `https://vita.cobblestonesystems.com/public/`
- **Format:** Web only — no API available
- **Use for:** checking state IT contract options alongside City contracts
- **Limitation:** Manual browsing or scraping only; no programmatic access

### USASpending.gov
- **What it is:** Federal spending transparency portal
- **URL:** `https://www.usaspending.gov/`
- **Format:** REST API (free, no key required for basic queries)
- **Use for:** federal spending data, contract award history by vendor or location
- **Verified:** API is publicly accessible

---

## Notes on Data Gaps

1. **No post-2018 RVA311 API** — the single largest data gap for the resident service navigation problem. The current platform (AvePoint/Dynamics 365) is closed.
2. **No pre-staged contract PDFs** — actual procurement document extraction requires sample PDFs that have not been provided. Teams building PDF extraction tools will need to source their own samples.
3. **No rva.gov structured data export** — website content must be crawled or scraped; no official data export exists.
4. **VITA portal is web-only** — no programmatic access to statewide IT contracts.
5. **SAM.gov requires API key registration** — budget time for this on day one of the hackathon.
