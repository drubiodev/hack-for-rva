# dataset_mapper

Purpose: Identify usable datasets, schemas, access paths, and gaps.

## When To Use
- Data needs are unclear or multiple sources exist.
- Before MVP scoping that depends on external data.

## Inputs
- Data index under `02_data/**` and any `data_sources.md`.
- Problem/MVP direction and target features.
- Known constraints (licenses, rate limits, privacy).

## Outputs
- Candidate datasets with links, ownership, and access notes.
- Schema snapshots (fields, keys) and integration considerations.
- Data quality risks, freshness, and mitigation steps.
- Prioritized shortlist aligned to MVP scope.

## Process
1) Scan `02_data/**` and repo notes; map datasets to user-facing features.
2) Describe acquisition method (API, CSV, portal) and schema highlights.
3) Call out quality and compliance risks; suggest quick validation steps.
4) Produce a prioritized list and recommend next actions.

