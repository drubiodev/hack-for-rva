---
name: research_search
description: Use when answering questions that require facts, evidence, personas, data sources, risks, or prior art from the Thriving Economy pillar research corpus. Use when a team asks about Richmond MBE contracting, small business formation, services, data availability, MVP feasibility, demo strategy, or risks — before answering from memory.
---

# research_search

## Overview

51 deep research files live in `research/`. Reading all of them is wasteful. This skill gives you a fast, two-step retrieval pattern: scan the index, read only what's relevant.

## Process

**Step 1 — Load the index (always)**

Read `research/index.json`. It is ~15KB and contains all 51 entries with `id`, `section`, `title`, `summary`, and `key_terms`.

**Step 2 — Identify relevant files**

Scan summaries and key_terms for terms matching the question. Select the 2–5 most relevant entries by `id`.

**Step 3 — Read those files**

Read `research/<id>.md` for each selected entry. These are the full research documents with citations.

**Step 4 — Answer with attribution**

Cite the source file when stating facts (e.g., "per A1_problem_landscape_mbe_contracting").

## Section Map (quick orientation)

| Section | Topic |
|---------|-------|
| `context` (00, 01) | Pillar framing, master prompt |
| `cross-cutting` (90–93) | Open questions, hypotheses, red flags, gaps |
| `A` (A1–A5) | Problem landscape |
| `B` (B1–B5) | Users and personas |
| `C` (C1–C5) | Services landscape |
| `D` (D1–D5) | Data inventory |
| `E` (E1–E5) | Prior art and benchmarks |
| `F` (F1–F5) | Opportunity spaces |
| `G` (G1–G5) | Risks and guardrails |
| `H` (H1–H5) | MVP feasibility |
| `I` (I1–I5) | Demo strategy |

## Common Query Patterns

| Question type | Start with |
|---------------|-----------|
| "What data exists for X?" | D1–D5 |
| "What has been tried elsewhere?" | E1–E5 |
| "Who is the user?" | B1–B5 |
| "What are the risks?" | G1–G5, 92 |
| "Is this MVP feasible?" | H1–H5 |
| "How should we demo this?" | I1–I5 |
| "What services already exist?" | C1–C5 |
| "What's the core problem?" | A1–A5 |
| "What should we NOT build?" | F5, 92, G1 |

## Rules

- **Never answer from memory** when the question is about Richmond-specific facts, programs, data, or disparity statistics. Always check the index first.
- If no relevant file exists, say so plainly — do not invent facts.
- The index summaries are approximations. When precision matters, read the full `.md`.
