---
name: parallel-data-enrichment
description: "Bulk data enrichment. Adds web-sourced fields (CEO names, funding, contact info) to lists of companies, people, or products. Supports multi-turn: pass --previous-interaction-id to continue with prior context."
user-invocable: true
argument-hint: <csv-file-or-inline-data>
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

## Data Enrichment

Enrich: $ARGUMENTS

### Step 1: Start enrichment

```bash
parallel-cli enrich run "$ARGUMENTS" --no-wait --json
```

For follow-ups chaining a prior interaction:

```bash
parallel-cli enrich run "$ARGUMENTS" --no-wait --json --previous-interaction-id "$INTERACTION_ID"
```

Parse the JSON output to extract `taskgroup_id`, `interaction_id`, and the monitoring URL. Tell the user enrichment has started and share the monitoring URL.

### Step 2: Poll for results

```bash
parallel-cli enrich poll "$TASKGROUP_ID" -o "$OUTPUT_FILE.csv" --timeout 540
```

- Use `--timeout 540` to stay within tool execution limits
- Results are written to the specified CSV output file
- Share the `interaction_id` for follow-up enrichment chaining

### Response format

After completion:
1. Confirm the output CSV path
2. Share the `interaction_id` for follow-up questions
3. Summarize what fields were enriched

### Setup

```bash
curl -fsSL https://parallel.ai/install.sh | bash
# or
pipx install "parallel-web-tools[cli]" && pipx ensurepath
parallel-cli login
# or: export PARALLEL_API_KEY="your-key"
```
