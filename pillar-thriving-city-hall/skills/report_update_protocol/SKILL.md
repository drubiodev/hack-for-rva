# report_update_protocol

Purpose: Safely add or update research reports and keep all metadata, indexes, and navigation files synchronized.

## When To Use
- Adding a new research report to the corpus
- Updating an existing report with new findings
- Correcting a factual error in a report
- Moving or renaming a file
- Adding a new section to the research corpus

## Inputs
- New or updated content to add
- Target location (section and filename)
- Any source citations or evidence to track

## Outputs
- Updated or new `.md` file with proper structure
- Updated `research/index.json` entry
- Updated `research/INDEX.md` row
- Updated `manifest.json` entry
- Optionally: updated `evidence_log.md` if new verified claims

## Process

### Step 1 — Locate or Name the File

For a **new report:**
1. Determine the correct section (A–I, or cross-cutting 90–98)
2. Choose the next available number in the section
3. Create the filename: `[SECTION][NUMBER]_[topic_slug].md`
4. Confirm no file with that name already exists

For an **existing report:**
1. Find the file in `research/`
2. Confirm it is the correct file (verify the H1 heading matches)
3. Note its current entry in `research/index.json` for comparison

### Step 2 — Prepare the File Content

Every report must:
- Begin with a clear H1 heading (the full report title)
- Contain only grounded claims (no invented data)
- Cite sources where possible (reference numbers from Parallel.ai are acceptable; include URLs if available)

Recommended frontmatter (add if not present):

```yaml
---
title: "Full Report Title"
pillar: thriving-city-hall
section: [A-I or cross-cutting]
problem_statement: service-navigation | procurement-review | general
tags:
  - [tag1]
  - [tag2]
summary: "1–2 sentence grounded summary of content."
geography: Richmond, VA
date_generated: YYYY-MM-DD
source: parallel-ai-pro | manual | other
status: raw | reviewed | verified
related_reports:
  - A1_problem_landscape_service_navigation
---
```

Only add fields you can fill accurately. Do not fabricate.

### Step 3 — Update `research/index.json`

Locate the file's entry (or create a new one):

```json
{
  "id": "SECTION_NUMBER_topic_slug",
  "section": "SECTION_LETTER",
  "title": "Human-Readable Title",
  "summary": "Accurate 1–2 sentence grounded summary from the actual content.",
  "key_terms": ["term1", "term2", "term3", "term4", "term5", "term6"]
}
```

Rules:
- `id` must match the filename (without `.md`)
- `summary` must reflect the actual content, not an invented description
- `key_terms` should be extractable from the report text
- For new files, insert in the correct section order (not appended to end)

### Step 4 — Update `research/INDEX.md`

Add a row to the correct section:

```markdown
- [`SECTION_N_topic_slug.md`](SECTION_N_topic_slug.md) — Short description of the report
```

For updated files, check whether the description still accurately represents the content.

### Step 5 — Update `manifest.json`

Add or update the entry in the root manifest:

```json
{
  "id": "research/SECTION_N_topic_slug",
  "path": "research/SECTION_N_topic_slug.md",
  "type": "research_report",
  "title": "Human-Readable Title",
  "pillar": "thriving-city-hall",
  "section": "SECTION_LETTER",
  "summary": "Accurate 1–2 sentence summary.",
  "tags": ["tag1", "tag2", "tag3"],
  "recommended_audience": ["describe who should read this and why"],
  "read_after": ["research/prerequisite_file.md"],
  "source_of_truth": true
}
```

### Step 6 — Update `evidence_log.md` (If Applicable)

If the report contains a newly verified factual claim (a claim with an official source URL):

Add a new row after the last E-015 entry:
```
| E-016 | [claim description] | [official URL] | [access date] | [notes] |
```

If the report verifies a previously listed unverified claim, update the existing row with the source URL and date rather than adding a duplicate.

### Step 7 — Run the Validation Check

Before committing:

```
[ ] File exists at expected path
[ ] H1 heading is accurate and matches frontmatter title
[ ] Frontmatter fields are grounded (no fabricated values)
[ ] research/index.json entry is accurate and valid JSON
[ ] research/INDEX.md row is present and accurate
[ ] manifest.json entry is present and valid JSON
[ ] Both JSON files pass: python3 -m json.tool [file]
[ ] evidence_log.md updated if new verified claims added
[ ] No broken internal links created
```

### Special Case: Renaming a File

Renaming an existing file requires updating all references. Run:

```bash
grep -r "OLD_FILENAME" . --include="*.md" --include="*.json"
```

Update every reference found before committing the rename. Pay particular attention to:
- `research/index.json` (`id` field)
- `manifest.json` (`id` and `path` fields)
- `research/INDEX.md` (link text and href)
- Any `related_reports` fields in other files' frontmatter
- `AGENTS.md` (if file is named there)
- `CORPUS_GUIDE.md` (if file is specifically referenced)

### Special Case: Removing a File

Before removing, check:
1. Is the file referenced in any navigation artifacts?
2. Is the file's content covered by another file?
3. Would removing it create a gap that agents would encounter?

Prefer deprecating over deleting: add a note to the file and its index entry rather than removing it outright.
