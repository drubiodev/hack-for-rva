---
name: parallel-deep-research
description: "ONLY use when user explicitly says 'deep research', 'exhaustive', 'comprehensive report', or 'thorough investigation'. Slower and more expensive than parallel-web-search. For normal research/lookup requests, use parallel-web-search instead. Supports multi-turn: pass --previous-interaction-id from a prior research or enrichment to continue with context."
user-invocable: true
argument-hint: <topic>
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

## Deep Research

Research topic: $ARGUMENTS

### When to use (vs parallel-web-search)

ONLY use this skill when the user explicitly requests deep/exhaustive research. Deep research is 10-100x slower and more expensive than parallel-web-search. For normal "research X" requests, quick lookups, or fact-checking, use **parallel-web-search** instead.

### Step 1: Start the research

```bash
parallel-cli research run "$ARGUMENTS" --processor pro-fast --no-wait --json
```

If this is a **follow-up** to a previous research or enrichment task where you know the `interaction_id`, add context chaining:

```bash
parallel-cli research run "$ARGUMENTS" --processor lite --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

This returns instantly. Do NOT omit `--no-wait` — without it the command blocks for minutes and will time out.

Processor options:

| Processor | Expected latency | Use when |
|-----------|-----------------|----------|
| `pro-fast` | 30s – 5 min | Default — good balance of depth and speed |
| `ultra-fast` | 1 – 10 min | Deeper analysis, more sources (~2x cost) |
| `ultra` | 5 – 25 min | Maximum depth, only when explicitly requested (~3x cost) |

Parse the JSON output to extract the `run_id`, `interaction_id`, and monitoring URL. Immediately tell the user:
- Deep research has been kicked off
- The expected latency for the processor tier chosen
- The monitoring URL where they can track progress

### Step 2: Poll for results

Choose a descriptive filename based on the topic. Use lowercase with hyphens, no spaces.

```bash
parallel-cli research poll "$RUN_ID" -o "$FILENAME" --timeout 540
```

Important:
- Use `--timeout 540` (9 minutes) to stay within tool execution limits
- Do NOT pass `--json` — the full output is large and will flood context
- The `-o` flag generates two output files:
  - `$FILENAME.json` — metadata and basis
  - `$FILENAME.md` — formatted markdown report
- The poll command prints an **executive summary** to stdout when complete. Share this with the user.

### If the poll times out

Re-run the same `parallel-cli research poll` command to continue waiting.

### Response format

**After step 1:** Share the monitoring URL.

**After step 2:**
1. Share the executive summary printed to stdout
2. Tell the user the two generated file paths
3. Share the `interaction_id` for follow-up chaining

Do NOT re-share the monitoring URL after completion.

### Setup

```bash
curl -fsSL https://parallel.ai/install.sh | bash
# or
pipx install "parallel-web-tools[cli]" && pipx ensurepath
parallel-cli login
# or: export PARALLEL_API_KEY="your-key"
```
