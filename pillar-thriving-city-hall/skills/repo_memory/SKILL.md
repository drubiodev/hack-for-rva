# repo_memory

Purpose: Reconstruct repository state and current stage.

## When To Use
- On wake or whenever context may be stale or missing.
- Before choosing or switching skills.

## Inputs
- Repository files: `project_one_pager.md`, `research_notes.md`, `evidence_log.md`, `data_sources.md`, `demo_script.md`.
- Knowledge dirs: `00_core/**`, `01_problem_space/**`, `02_data/**`, `04_build_guides/**`, `05_prompts/**`, `99_templates/**`.
- Optional: user-provided hints (pillar, intended stage).

## Outputs
- Stage guess: `orientation | research | problem_selection | mvp_design | build | demo_preparation`.
- 5-bullet progress summary of artifacts found.
- List of blockers/unknowns.
- Pointers to key files/paths.

## Process
1) Scan repo for canonical artifacts and note presence/recency.
2) Infer stage based on artifacts present and completeness.
3) Summarize current state and enumerate unknowns that block progress.
4) Recommend the next suitable skill (do not execute without confirmation).

