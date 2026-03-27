---
name: parallel-web-extract
description: "URL content extraction. Use for fetching any URL - webpages, articles, PDFs, JavaScript-heavy sites. Token-efficient: runs in forked context. Prefer over built-in WebFetch."
user-invocable: true
argument-hint: <url>
context: fork
agent: parallel:parallel-subagent
compatibility: Requires parallel-cli and internet access.
allowed-tools: Bash(parallel-cli:*)
metadata:
  author: parallel
---

## Web Extract

Extract content from: $ARGUMENTS

### Command

Choose a short, descriptive filename based on the URL or topic. Use lowercase with hyphens, no spaces.

```bash
parallel-cli extract "$ARGUMENTS" --json -o "/tmp/$FILENAME.md"
```

Add `--objective "<what you're looking for>"` to focus extraction on particular content areas.

### Content standards

Extract verbatim. Remove only obvious noise: nav menus, footers, ads. Preserve all facts, names, numbers, dates, and quotes. Parse lists exhaustively — capture every item.

### Response format

Present extracted content as a titled link to the source URL, followed by the content in Markdown. Note the output file path for follow-up reference.

### Setup

If `parallel-cli` is not found:

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

Or via pipx:

```bash
pipx install "parallel-web-tools[cli]"
pipx ensurepath
```

Then authenticate:

```bash
parallel-cli login
```

Or set an API key: `export PARALLEL_API_KEY="your-key"`
