# Problem Selection Prompt — A Thriving City Hall

Use this prompt to help your team choose a strong problem to work on for the hackathon.

---

## Before using this prompt

Read:
- `01_problem_space/02_targeted_problem_statements.md` (both targeted problems)
- `01_problem_space/01_bluesky_problem_statements.md` (blue sky ideas)
- `00_core/00_pillar_overview.md`
- `QUICKSTART.md` (critical constraints, especially the RVA311 API gap)

---

## Prompt to run (with Hackbot or an LLM of your choice)

```
I am working on the A Thriving City Hall pillar at the Richmond Civic Hackathon (March 27-29, 2026 at VCU Snead Hall).

The pillar has two targeted problem statements:
1. Helping Residents Find the Right City Service or Next Step (Score: 27/32)
2. Helping City Staff Review Procurement Risks and Opportunities (Score: 22/32)

It also has blue sky statements including:
- Unified Digital Front Door (20/27)
- Making Fiscal Responsibility More Visible (21/27)
- Better Communication Between City and Residents (19/27)

My team's skills and constraints:
[FILL IN: describe your team's skills — e.g., "2 Python developers, 1 UX designer, 1 product manager; 48 hours; no access to City systems"]

Based on the problem statements and my team's constraints, help me:
1. Rank the two targeted problem statements for my team's specific skills and situation
2. Identify the most buildable weekend MVP shape for each
3. Flag any risks or blockers I should know about before choosing
4. Recommend which problem to pursue and why

Key constraints to factor in:
- RVA311 (AvePoint Citizen Services) has NO public API — post-2018 311 data is not accessible
- Historical 311 Socrata data covers only January 2014–August 2015
- The City Contracts Socrata API has a known column bug — use the CSV download
- Any tool must work with existing City systems, not replace or claim to integrate with them
- Prototypes must be demoable by Sunday afternoon
```

---

## What to do with the output

1. Review the ranking and rationale
2. Have your team vote on the top choice
3. Record your decision in `99_templates/decision_memo.md`
4. Proceed to Phase 3 (Research) in the README

---

## Red flags to watch for in the output

If the LLM suggests any of the following, push back:
- "Integrate with the AvePoint/RVA311 API" — this API does not exist publicly
- "Pull live 311 request data" — no public access to post-2018 data
- "Automate procurement decisions or compliance checks" — out of scope and risky
- "Build a chatbot that handles any City service question" — overclaimed scope
- Tools requiring City system access, City staff cooperation during the hackathon, or private data
