---
description: Set up or troubleshoot the Claude Code GitHub Action for team agents — handles workflow config, secrets, permissions, and the official Claude GitHub App
---

Guide the user through setting up or fixing the Claude Code GitHub Action (`anthropics/claude-code-action@v1`) so that team agents can be triggered via `@claude` mentions in issues, PRs, and review comments.

---

## Step 1: Verify prerequisites

Check the following:

1. **Workflow file exists** — `.github/workflows/claude.yml` should be committed to the repo. Read it and confirm it uses `anthropics/claude-code-action@v1`.
2. **Repository is on GitHub** — run `git remote -v` and confirm a GitHub remote exists.
3. **User has admin access** — required to install the GitHub App and configure secrets.

If any prerequisite is missing, tell the user what they need before proceeding.

---

## Step 2: Install the Claude GitHub App

There are two options:

### Option A: Official Claude App (simplest)

1. Direct the user to install: https://github.com/apps/claude
2. Select the target repository (or all repositories)
3. Approve the requested permissions

### Option B: Custom GitHub App (advanced)

1. Create a new GitHub App at https://github.com/settings/apps
2. Set minimum permissions:
   - **Contents**: Read & Write
   - **Issues**: Read & Write
   - **Pull requests**: Read & Write
3. Generate and download a private key (`.pem` file)
4. Install the app on target repositories
5. Add these secrets to the repo:
   - `APP_ID` — the app's numeric ID
   - `APP_PRIVATE_KEY` — contents of the `.pem` file
6. Update `.github/workflows/claude.yml` to use token generation:

```yaml
steps:
  - name: Generate GitHub App token
    id: app-token
    uses: actions/create-github-app-token@v1
    with:
      app-id: ${{ secrets.APP_ID }}
      private-key: ${{ secrets.APP_PRIVATE_KEY }}

  - uses: anthropics/claude-code-action@v1
    with:
      anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
      github_token: ${{ steps.app-token.outputs.token }}
```

---

## Step 3: Configure secrets

Guide the user to add the required secret(s) in GitHub:

1. Go to **Settings > Secrets and variables > Actions** in the GitHub repo
2. Click **New repository secret**
3. Add `ANTHROPIC_API_KEY` with their Anthropic API key value

For OAuth users (Pro/Max plans), they can use `CLAUDE_CODE_OAUTH_TOKEN` instead.

**Security reminders:**
- Never commit API keys to the repository
- Always reference secrets via `${{ secrets.NAME }}`
- Rotate credentials regularly

---

## Step 4: Test the integration

1. Push the workflow file to the default branch
2. Create a test issue with `@claude` in the body (e.g., "Hey @claude, summarize this repo")
3. Check the **Actions** tab to see if the workflow triggered
4. If it didn't trigger, check:
   - Is the workflow on the default branch?
   - Does the GitHub App have the correct permissions?
   - Are the secrets configured?

---

## Step 5: Optional configuration

Explain these optional settings if the user asks:

| Setting | Purpose |
|---|---|
| `trigger_phrase` | Change from `@claude` to a custom trigger |
| `assignee_trigger` | Trigger when a specific user is assigned to an issue |
| `claude_args` | Pass CLI args like `--model`, `--max-turns`, `--allowedTools`, `--system-prompt` |
| `settings` | JSON block for env vars and other Claude Code settings |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Workflow doesn't trigger | Ensure workflow is on default branch; check `if` conditions match event |
| 401/403 from Anthropic | Verify `ANTHROPIC_API_KEY` secret is set and valid |
| Claude can't push commits | Check `contents: write` permission in workflow |
| Claude can't comment | Check `issues: write` and `pull-requests: write` permissions |
| "Resource not accessible by integration" | GitHub App needs to be installed on this specific repo |
| App install fails ("Failed to access repository") | User may not have admin access, or repo is in an org that restricts app installs |

---

## Output

After setup, confirm:
- Workflow file path and trigger conditions
- Which secrets need to be set (and which are already configured)
- Next step the user should take (e.g., "push to main and create a test issue")
