# Research Notes — A Thriving City Hall

Note: All facts in this section are marked [Unverified] unless confirmed with an official source and logged in `evidence_log.md`. This document should be updated as research is completed.

---

## Executive Brief (update as research is completed)

This section is for confirmed, source-linked findings. Leave blank until research is verified.

---

## Domain Notes (Unverified)

### 311 System Architecture

[Unverified] Richmond's RVA311 system launched on June 15, 2018, replacing the SeeClickFix platform that had been in use since approximately 2014. The new platform uses AvePoint Citizen Services, built on Microsoft Dynamics 365 and hosted on Azure.

[Unverified] The current system handles approximately 208,216 service requests annually (2025 figure from rubric document). Request types are organized into approximately 50+ categories across 7 department groups.

[Unverified] The integration chain runs: Citizen → RVA311 (Dynamics 365) → Microsoft BizTalk (integration middleware) → Trimble Cityworks (DPW work order system). Non-DPW requests presumably follow different routing paths.

[Unverified] The AvePoint Citizen Services platform does not expose a public API. This is the single most significant data constraint for building resident service navigation tools. The decision not to publish to Socrata means there is no programmatic access to post-2018 311 data.

[Unverified] The historical SeeClickFix data on Socrata (dataset vgg4-hjn8) covers only January 2014 through August 2015. It was produced by a different platform with a different category taxonomy. Its value for understanding current 311 routing patterns is limited.

### rva.gov Drupal Structure

[Unverified] Richmond's city website (rva.gov) runs Drupal 8+ on Acquia cloud hosting, developed and maintained by Tech Dynamism, a contractor. The site uses the Drupal Search API module with the Facets module for filtered search.

[Unverified] The search URL pattern is: https://www.rva.gov/search?search={query}&page={n}&f[0]=business_unit:{id}. The "business_unit" facet allows filtering by department. Over 40 department slug identifiers exist, though the complete list is not publicly documented in a single place.

[Unverified] rva.gov supports translation into 36 languages using Google Translate widget. Translation quality for government service terminology (department names, service categories, permit types) may be inconsistent.

[Unverified] The site's information architecture is department-centric — pages are organized around department structure rather than around citizen tasks or needs. This is the root cause of the navigation problem identified in the problem statement.

### Procurement Data Landscape

[Unverified] Richmond maintains a public City Contracts dataset on Socrata (dataset ID xqn7-jvv2) with records dating back to approximately January 2011. The dataset has 9 columns, but there is a known bug in the SODA REST API where only 8 columns are returned. The complete 9-column dataset can be accessed via CSV download at: data.richmondgov.com/api/views/xqn7-jvv2/rows.csv?accessType=DOWNLOAD

[Unverified] VITA (Virginia IT Agency) maintains a statewide contract portal at vita.cobblestonesystems.com/public/. This portal lists statewide IT contracts but has no programmatic API — data must be accessed through manual browsing or web scraping.

[Unverified] SAM.gov (System for Award Management) provides free API access to federal contract and vendor data. A free API key can be obtained through the SAM.gov registration process. Key data available includes contract awards, vendor registrations, and exclusions (debarment) data.

[Unverified] eVA (Virginia electronic procurement) data is available as a CSV download via data.virginia.gov. The exact dataset URL and schema are not confirmed in this repository.

[Unverified] Richmond's internal procurement and financial system is Oracle RAPIDS. This system is not publicly accessible.

### Known Gaps

The following information gaps are significant for hackathon planning:
1. No post-2018 RVA311 data of any kind is publicly accessible
2. Sample procurement PDFs are not pre-staged
3. The 311 routing decision logic is not documented publicly
4. The rva.gov sitemap availability is unconfirmed
5. The complete department slug list for rva.gov search facets is not documented

---

## Research Log

Use this section to track which research prompts have been run and key findings.

| Prompt | Date Run | Key Finding | Evidence Log ID |
|--------|----------|-------------|-----------------|
| (none yet) | | | |
