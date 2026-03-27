# Agent Teams Reference Guide

> Quick reference for using Claude Code agent teams in this project.
> Based on [official docs](https://code.claude.com/docs/en/agent-teams).

## Setup

Agent teams are experimental. Enable by adding to your `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Requires Claude Code v2.1.32+.

## When to Use Agent Teams vs Subagents

| Use agent teams when... | Use subagents when... |
|---|---|
| Teammates need to share findings and challenge each other | You need focused workers that report back results |
| Complex work requiring discussion and collaboration | Only the final result matters |
| Parallel exploration adds real value (research, review, debugging) | Sequential or same-file work |

**Rule of thumb:** If workers need to talk to _each other_, use teams. If they just report back, use subagents.

## Starting a Team

Describe the task and team structure in natural language:

```text
Create an agent team to [task]. Spawn [N] teammates:
- One focused on [role A]
- One focused on [role B]
- One focused on [role C]
```

## Project-Specific Team Recipes

These recipes are tailored to the 311 SMS service architecture.

### Full-Stack Feature Development

```text
Create an agent team with 3 teammates to implement [feature]:
- Backend teammate: implement the FastAPI endpoint per docs/openapi.yaml.
  Follow the patterns in the existing backend code.
- Frontend teammate: build the React component consuming the API.
  Follow the patterns in the existing frontend code.
- Test teammate: write e2e tests covering the happy path and error cases.
Have them coordinate via task list. Backend should finish the endpoint
before frontend integrates.
```

### Parallel Code Review

```text
Create an agent team to review PR #[N]. Spawn three reviewers:
- Security reviewer: check for injection, auth issues, secrets exposure.
  Reference .claude/skills/security-audit.md criteria.
- Architecture reviewer: verify alignment with docs/technical-implementation-plan.md
  and docs/openapi.yaml. Flag any architectural drift.
- Quality reviewer: check test coverage, error handling, and code style.
Have them each report findings with severity ratings.
```

### Debugging with Competing Hypotheses

```text
[Describe the bug]. Spawn 3-5 agent teammates to investigate different
hypotheses. Have them talk to each other to try to disprove each other's
theories. Update findings as consensus emerges.
```

### Research and Spike

```text
Create an agent team to research [topic] from different angles:
- One teammate on implementation approach A
- One teammate on implementation approach B
- One playing devil's advocate, stress-testing both approaches
Have them debate trade-offs and synthesize a recommendation.
```

## Display Modes

| Mode | Setting | When to use |
|---|---|---|
| **In-process** (default) | `"teammateMode": "in-process"` | Works in any terminal including VS Code |
| **Split panes** | `"teammateMode": "tmux"` | Need to see all teammates at once (requires tmux or iTerm2) |
| **Auto** | `"teammateMode": "auto"` | Uses split panes if already in tmux, otherwise in-process |

Override per session: `claude --teammate-mode in-process`

### In-Process Navigation

- **Shift+Down** — cycle through teammates
- **Enter** — view a teammate's session
- **Escape** — interrupt a teammate's current turn
- **Ctrl+T** — toggle the task list

## Controlling the Team

### Specify models for teammates

```text
Create a team with 4 teammates. Use Sonnet for each teammate.
```

### Require plan approval

```text
Spawn an architect teammate to refactor [module].
Require plan approval before they make any changes.
Only approve plans that include test coverage.
```

### Talk to teammates directly

In-process: **Shift+Down** to select a teammate, then type your message.
Split panes: click into a teammate's pane.

### Shut down a teammate

```text
Ask the [name] teammate to shut down
```

### Clean up the team

```text
Clean up the team
```

Always shut down all teammates before cleanup. Only the lead should run cleanup.

## Task Management

Tasks have three states: **pending**, **in progress**, **completed**. Tasks can have dependencies — blocked tasks auto-unblock when their dependencies complete.

- The lead creates and assigns tasks automatically
- Teammates self-claim the next unassigned, unblocked task when done
- If the lead isn't creating enough tasks: _"Split the work into smaller pieces"_
- If the lead starts doing work itself: _"Wait for your teammates to complete their tasks before proceeding"_

**Sizing guideline:** 5-6 tasks per teammate. Aim for self-contained units that produce a clear deliverable (a function, a test file, a review).

## Best Practices

1. **Start with 3-5 teammates** — more than that has diminishing returns and higher coordination overhead
2. **Give teammates enough context** — they load CLAUDE.md and skills but NOT the lead's conversation history. Put task-specific details in the spawn prompt
3. **Avoid file conflicts** — each teammate should own different files. Don't have two teammates editing the same file
4. **Monitor and steer** — check in on progress, redirect approaches that aren't working
5. **Start with read-only tasks** — if new to teams, begin with reviews or research before attempting parallel implementation
6. **Pre-approve common permissions** — teammate permission requests bubble up to the lead, creating friction. Pre-approve in your permission settings

## Quality Gates with Hooks

Use hooks to enforce rules automatically:

| Hook | Fires when... | Exit code 2 to... |
|---|---|---|
| `TeammateIdle` | Teammate is about to go idle | Send feedback, keep them working |
| `TaskCreated` | A task is being created | Prevent creation with feedback |
| `TaskCompleted` | A task is being marked complete | Prevent completion with feedback |

## Known Limitations

- **No session resumption** — `/resume` and `/rewind` don't restore in-process teammates
- **One team per session** — clean up before starting a new team
- **No nested teams** — teammates can't spawn their own teams
- **Lead is fixed** — can't transfer leadership
- **Permissions set at spawn** — all teammates inherit the lead's mode (changeable individually after)
- **Split panes not supported** in VS Code terminal, Windows Terminal, or Ghostty
- **Task status can lag** — if a task looks stuck, nudge the teammate or update manually

## Troubleshooting

| Problem | Fix |
|---|---|
| Teammates not appearing | Press Shift+Down; they may be running but not visible |
| Too many permission prompts | Pre-approve common operations in permission settings |
| Teammate stops on error | Message them directly with instructions, or spawn a replacement |
| Lead shuts down too early | Tell it to wait for teammates to finish |
| Orphaned tmux sessions | `tmux ls` then `tmux kill-session -t <name>` |

## Token Cost Awareness

Each teammate is a separate Claude instance with its own context window. Token usage scales linearly with team size. Use teams when parallel exploration justifies the cost — for routine tasks, a single session or subagents are more efficient.
