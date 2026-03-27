---
title: "RVA311 (2014–2015) Socrata: What’s Usable Now, What’s Not"
pillar: thriving-city-hall
section: D
problem_statement: service-navigation
tags:
  - RVA311
  - Socrata
  - SeeClickFix
  - historical-data
  - vgg4-hjn8
  - data-schema
summary: "Field-by-field schema analysis of the RVA311 historical Socrata dataset (vgg4-hjn8): 43,273 SeeClickFix records from Jan 2014–Aug 2015. Documents what is usable for prototypes and why it cannot represent current RVA311 operations."
geography: Richmond, VA
source: parallel-ai-pro
status: raw
related_reports:
  - D2_data_contracts
  - D4_data_rvagov_content
  - C1_services_311_landscape
---

# RVA311 (2014–2015) Socrata: What’s Usable Now, What’s Not

## Executive Summary
The RVA311 Historical Socrata dataset (vgg4-hjn8) provides a functional, albeit historically bounded, snapshot of Richmond's civic service requests from January 2014 through August 2015. Containing exactly 43,273 records [1], the dataset is complete enough to build working prototypes for civic tech applications, particularly around waste management and street repair. However, it is strictly a legacy SeeClickFix-era asset. Because the City of Richmond migrated to a new RVA311 system in 2018 (and upgraded it in 2021) that expanded request types from 6-8 to nearly 70 [2], this dataset **cannot** be used as a proxy for current 311 operations, category taxonomies, or modern service level agreements (SLAs). 

For hackathon teams, the immediate value lies in the high volume of "Trash/Bulk Pick-ups" and "Potholes" requests [1], which offer excellent training data for spatial clustering and natural language processing (NLP) models, provided developers navigate the dataset's specific quirks regarding geographic nulls and archival status flags.

## Scope and Provenance Anchored
This dataset represents a specific 20-month operational window. It contains 43,273 total rows and 19 base columns [3]. The data originates from the SeeClickFix platform, which the city used before launching its dedicated RVA311 portal [2]. Treat this dataset as a historical slice with consistent structure, not a live mirror of current operations.

## Field-by-Field Schema You Can Code Against
The dataset contains 19 base columns and 2 computed georegion columns [1]. A well-defined schema enables quick ingestion, but developers must watch for literal "NULL" strings and nested location objects.

| Column Name | Data Type | Example Value | Nulls / Notes |
| :--- | :--- | :--- | :--- |
| `SCFId` | number | 1521548 | 0 nulls. Unique SeeClickFix ID [1] [4]. |
| `ReporterDisplayName` | text | "City of Richmond" | 0 nulls. Contains PII (names, emails) [1]. |
| `Status` | text | "Archived" | 0 nulls. Nonstandard lifecycle [1]. |
| `Summary` | text | "Trash/Bulk Pick-ups" | 0 nulls. Short label/category-like [1]. |
| `Rating` | number | 3 | 0 nulls. Ambiguous scale (mostly 2–3, max 72) [1]. |
| `Description` | text | "sidewalk needs repair" | 780 nulls. Narrative text [1] [4]. |
| `Notes` | text | "SLC-Citizen contacted..." | 32,614 nulls. Closure notes [1]. |
| `CreatedDate` | calendar_date | 2015-03-10T07:19:00.000 | 0 nulls [4]. |
| `Closed` | calendar_date | 2015-03-11T02:40:00.000 | 0 nulls [4]. |
| `Precinct` | number | 4 | 128 nulls [1]. |
| `CouncilDistrict` | number | 5 | 28,683 nulls [1]. |
| `Sector` | number | 311 | 28,683 nulls [1]. |
| `Neighborhood` | text | "The Fan" | 0 true nulls, but 28,683 literal "NULL" strings [1]. |
| `ReportedUsingMobile` | number | 0 | 0 nulls. Binary (0 or 1) [1]. |
| `RequestTypeId` | number | 1330 | 0 nulls. Maps to Category [1]. |
| `RequestTypeAnswers` | text | "Q: What type of pickup..." | 18,709 nulls. Contains PII [1]. |
| `Category` | text | "Other" | 0 nulls. 9 distinct categories [1]. |
| `ObjectID` | number | 120313 | 0 nulls. Unique row ID [1]. |
| `Location_1` | location | `{"latitude":"37.588802"...}` | Contains lat/long and human_address JSON [4]. |
| `:@computed_region_mcva_69mv` | number | 10116 | Zip code join [4]. |
| `:@computed_region_m85f_c8dc` | number | 5 | Neighborhood join [4]. |

## Time Coverage and Volume
The dataset spans exactly 20 months of activity. 
* **First Created Record:** 2014-01-01T04:56:00.000 [1]
* **Last Created Record:** 2015-08-25T04:32:00.000 [1]
* **First Closed Record:** 2014-01-02T07:16:00.000 [1]
* **Last Closed Record:** 2015-08-26T01:21:00.000 [1]

Use `createddate` for primary temporal grouping. Any performance claims or models built on this data must explicitly document this 20-month historical window.

## Category Taxonomy and Mapping
Volume is heavily concentrated in waste and road issues. The `RequestTypeId` cleanly maps to the `Category` field.

| Category | Count | Percentage | RequestTypeId |
| :--- | :--- | :--- | :--- |
| Trash/Bulk Pick-ups | 23,379 | 54.0% | 275 [1] |
| Potholes | 6,246 | 14.4% | 273 [1] |
| Other | 4,487 | 10.4% | 1330 [1] |
| Overgrown Lots | 3,166 | 7.3% | 288 [1] |
| Non-functioning Street Lights | 3,086 | 7.1% | 272 [1] |
| Illegal Dumping | 1,479 | 3.4% | 291 [1] |
| Abandoned Cars | 687 | 1.6% | 274 [1] |
| Open and Vacant Properties | 414 | 1.0% | 375 [1] |
| Non-functioning Traffic Lights | 329 | 0.8% | 290 [1] |

**Takeaway:** Build classifiers on Category using Summary and Description fields. Treat "Other" as a multi-intent category, as it contains significant heterogeneity.

## Status Model and Resolution Timing
The `Status` field is archival and should not be used to infer operational resolution rates. 

| Status Value | Count |
| :--- | :--- |
| Archived | 42,234 [1] |
| Closed | 915 [1] |
| Acknowledged | 120 [1] |
| Open | 4 [1] |

**Takeaway:** Because 97.6% of records are marked "Archived," this field is operationally meaningless for modern analysis. To calculate resolution timing, compute the duration between `closed` and `createddate`. Never equate "Archived" to "Resolved."

## Geography That Works
The `location_1` field is your geospatial source of truth. Legacy administrative tags are highly incomplete.

* **The Problem:** `CouncilDistrict` and `Sector` are missing in 28,683 records (66%) [5]. The `Neighborhood` field stores the literal string "NULL" in 28,683 rows [1].
* **The Solution:** Use `location_1` for mapping, as it provides reliable latitude and longitude [4]. Clean the "NULL" strings up front, and rely on the provided computed_region columns (`:@computed_region_mcva_69mv` and `:@computed_region_m85f_c8dc`) for choropleth mapping [1].

## Data Completeness and Quality
While core fields are robust, secondary text fields and administrative boundaries suffer from high sparsity.

| Field | Missing / Null Count | Percentage Missing |
| :--- | :--- | :--- |
| Description | 780 | 1.8% [6] |
| Notes | 32,614 | 75.4% [6] |
| RequestTypeAnswers | 18,709 | 43.2% [7] |
| Precinct | 128 | 0.3% [5] |
| CouncilDistrict | 28,683 | 66.3% [5] |
| Sector | 28,683 | 66.3% [5] |

**Takeaway:** Descriptions are mostly present, making NLP viable. However, closure notes are too sparse to be reliable. Furthermore, `RequestTypeAnswers` and `ReporterDisplayName` frequently contain PII (emails and phone numbers) [1]. Run a PII scrubber on all text fields before public demos. Additionally, the `Rating` field is ambiguous (ranging from 2 to 72) and should be excluded from satisfaction metrics [1].

## SODA API: How to Pull Reliably
API access is reliable but bounded. Design queries to be cheap and paginated.
* Use `$offset` for pagination and always `$order` by an indexed field (e.g., `objectid`).
* Heavy `$select`, `$group`, or `$order` queries may time out. Pre-aggregate where possible.
* For hackathons, prefetch the dataset to CSV/Parquet or register an app token to reduce throttling.

## Fit for Today (2018+ RVA311)
The category taxonomy from 2014–2015 **cannot** be used as a proxy for current 311 categories. The system has changed significantly. Before RVA311 launched in 2018, the city used SeeClickFix, which only had 6 to 8 request types [2]. The modern RVA311 system is approaching 70 distinct request types [2]. 

Do not map 2014–2015 categories to today’s without a reconciliation step. If you must use them, present them strictly as a "historical grouping."

## Hackathon Playbook
Ship targeted demos with strong caveats, scrub PII, and document limitations.

* **Recommended Sprints:**
 1. **Waste Heatmap:** Build a pickup backlog estimator using `createddate` clusters for the 23,379 Trash/Bulk requests [1].
 2. **Pothole Classifier:** Train a model using `Summary` and `Description` text to identify road hazards.
 3. **Channel Analysis:** Compare the 5,062 mobile requests against the 38,211 non-mobile requests [8] to analyze reporting behaviors.
* **Data Prep:** Normalize the `Neighborhood` field ("NULL" -> actual null), recompute regions from `location_1`, and mask PII in `RequestTypeAnswers` [1].

## What This Dataset Cannot Tell You
Avoid overreach. This dataset provides no reliable view into current RVA311 operations. It cannot support analyses of:
* Current request taxonomy or volumes (post-2018).
* Modern closure performance versus targets.
* Departmental workload mix today.
* Citizen satisfaction trends (the `Rating` field is not a standard CSAT score) [1].

## Appendix
**Sample Record Structure:**
```json
[{
 "scfid": "1521548",
 "reporterdisplayname": "Marie423",
 "status": "Archived",
 "summary": "Other",
 "rating": "3",
 "description": "sidewalk needs repair",
 "createddate": "2015-03-10T07:19:00.000",
 "closed": "2015-03-11T02:40:00.000",
 "precinct": "4",
 "neighborhood": "NULL",
 "reportedusingmobile": "0",
 "requesttypeid": "1330",
 "category": "Other",
 "objectid": "120313",
 "location_1": {
 "latitude": "37.588802",
 "longitude": "-77.454059",
 "human_address": "{\"address\": \"1305 Nottoway Ave Richmond, Virginia\", \"city\": \"\", \"state\": \"\", \"zip\": \"\"}"
 },
 ":@computed_region_mcva_69mv": "10116",
 ":@computed_region_m85f_c8dc": "5"
}]
```
*(Source: [4])*

## References

1. *Fetched web page*. https://data.richmondgov.com/api/views/vgg4-hjn8
2. *Richmond Launches New App to Let Residents Report Problems*. https://www.vpm.org/news/2021-03-16/richmond-launches-new-app-to-let-residents-report-problems
3. *SeeClickFix Sample Data Aug 2014 to Aug 2015 | Open Data Portal | City of Richmond, Virginia*. https://data.richmondgov.com/d/vgg4-hjn8
4. *Fetched web page*. https://data.richmondgov.com/resource/vgg4-hjn8.json?$limit=1
5. *Fetched web page*. https://data.richmondgov.com/resource/vgg4-hjn8.json?$select=count(1)-count(councildistrict)%20as%20null_councildistrict,count(1)-count(sector)%20as%20null_sector,count(1)-count(precinct)%20as%20null_precinct
6. *Fetched web page*. https://data.richmondgov.com/resource/vgg4-hjn8.json?$select=count(1)-count(description)%20as%20null_description,count(1)-count(notes)%20as%20null_notes
7. *Fetched web page*. https://data.richmondgov.com/resource/vgg4-hjn8.json?$select=count(1)-count(requesttypeanswers)%20as%20null_requesttypeanswers
8. *Fetched web page*. https://data.richmondgov.com/resource/vgg4-hjn8.json?$select=reportedusingmobile,count(1)%20as%20count&$group=reportedusingmobile&$order=reportedusingmobile