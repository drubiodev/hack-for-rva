# research_runner

Purpose: Execute research prompts and collect findings with sources.

## When To Use
- You need evidence to validate a problem, users, services, data, or feasibility.
- Before MVP design or when claims require citations.

## Inputs
- Prompt IDs or folder under `05_prompts/research/**`.
- Perplexity runner: `05_prompts/perplexity_runner/**` (config, API key).
- Optional per-prompt overrides (YAML or front matter).
- Specific research questions or hypotheses (if provided by user).

## Outputs
- Brief findings summary per prompt with Richmond-specific sources.
- Consolidated evidence log with links and short notes.
- Saved raw outputs to `05_prompts/perplexity_runner/research-output/` (if approved).

## Process
1) Confirm prompts to run and any overrides; verify API key availability.
2) Run prompts via the runner; capture responses and source links.
3) Extract key evidence; note contradictions, gaps, and red flags.
4) Produce a concise summary; point to saved artifacts if writing was approved.
5) Flag any eligibility/legal claims and escalate to `risk_review` if needed.

