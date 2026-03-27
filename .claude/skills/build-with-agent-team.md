---
name: build-with-agent-team
description: Build a project using Claude Code Agent Teams with tmux split panes. Takes a plan document path and optional team size. Use when you want multiple agents collaborating on a build.
argument-hint: [plan-path] [num-agents]
disable-model-invocation: false
---

# Build with Agent Team

You are coordinating a build using Claude Code Agent Teams. Read the plan document, determine the right team structure, spawn teammates, and orchestrate the build.

## Arguments

- **Plan path**: `$ARGUMENTS[0]` - Path to a markdown file describing what to build
- **Team size**: `$ARGUMENTS[1]` - Number of agents (optional)

## Step 1: Read the Plan

Read the plan document at `$ARGUMENTS[0]`. Understand:
- What are we building?
- What are the major components/layers?
- What technologies are involved?
- What are the dependencies between components?

Also read `CLAUDE.md` for project guardrails and architecture constraints that all agents must follow.

## Step 2: Determine Team Structure

If team size is specified (`$ARGUMENTS[1]`), use that number of agents.

If NOT specified, analyze the plan and determine the optimal team size based on:
- **Number of independent components** (frontend, backend, database, infra, etc.)
- **Technology boundaries** (different languages/frameworks = different agents)
- **Parallelization potential** (what can be built simultaneously?)

**Guidelines:**
- 2 agents: Simple projects with clear frontend/backend split
- 3 agents: Full-stack apps (frontend, backend, database/infra)
- 4 agents: Complex systems with additional concerns (testing, DevOps, docs)
- 5+ agents: Large systems with many independent modules

For each agent, define:
1. **Name**: Short, descriptive (e.g., "frontend", "backend", "database")
2. **Ownership**: What files/directories they own exclusively
3. **Does NOT touch**: What's off-limits (prevents conflicts)
4. **Key responsibilities**: What they're building

## Step 3: Set Up Agent Team

Enable tmux split panes so each agent is visible:

```
teammateMode: "tmux"
```

## Step 4: Define Contracts

Before spawning agents, the lead reads the plan and defines the integration contracts between layers. This focused upfront work is what enables all agents to spawn in parallel without diverging on interfaces. Agents that build in parallel will diverge on endpoint URLs, response shapes, trailing slashes, and data storage semantics unless they start with agreed-upon contracts.

### Map the Contract Chain

Identify which layers need to agree on interfaces:

```
Database → function signatures, data shapes → Backend
Backend → API contract (URLs, response shapes, SSE format) → Frontend
```

**For this project**: `docs/openapi.yaml` is the single source of truth for the backend/frontend contract. All agents must conform to it. If it doesn't exist yet, the lead must author it before spawning.

### Author the Contracts

From the plan, define each integration contract with enough specificity that agents can build to it independently:

**Database → Backend contract:**
- Function signatures (create, read, update, delete)
- Pydantic model definitions
- Data shapes and types

**Backend → Frontend contract:**
- Exact endpoint URLs (including trailing slash conventions)
- Request/response JSON shapes (exact structures, not prose descriptions)
- Status codes for success and error cases
- SSE event types with exact JSON format (if applicable)
- Response envelopes (flat vs nested)

### Identify Cross-Cutting Concerns

Some behaviors span multiple agents and will fall through the cracks unless explicitly assigned. Identify these from the plan and assign ownership to one agent:

Common cross-cutting concerns:
- **URL conventions**: Trailing slashes, path parameters, query params — both sides must match exactly
- **Response envelopes**: Flat objects vs nested wrappers — both sides must agree
- **Error shapes**: How errors are returned (status codes, error body format)
- **Environment variables**: Both backend and frontend need consistent config
- **Phone number masking**: No full phone numbers in API responses (project guardrail)

Assign each concern to one agent with instructions to coordinate with others.

### Contract Quality Checklist

Before including a contract in agent prompts, verify:
- Are URLs exact, including trailing slashes?
- Are response shapes explicit JSON, not prose descriptions?
- Are error responses specified? (404 body, 422 body, etc.)
- Does the contract match `docs/openapi.yaml` (if it exists)?

## Step 5: Spawn All Agents in Parallel

With contracts defined, spawn all agents simultaneously. Each agent receives the full context they need to build independently from the start.

Enter **Delegate Mode** (Shift+Tab) before spawning. You should not implement code yourself — your role is coordination.

### Spawn Prompt Structure

```
You are the [ROLE] agent for this build.

## Project Context
Read CLAUDE.md for architecture guardrails. These are non-negotiable:
- No LangGraph — plain Python state machine
- No Celery / No Redis — FastAPI BackgroundTasks + in-memory dict
- GPT-4.1-nano for classification, GPT-4o-mini for response generation
- docs/openapi.yaml is the single source of truth
- No full phone numbers in API responses

## Your Ownership
- You own: [directories/files]
- Do NOT touch: [other agents' files]

## What You're Building
[Relevant section from plan]

## Contracts

### Contract You Produce
[Include the lead-authored contract this agent is responsible for]
- Build to match this exactly
- If you need to deviate, message the lead and wait for approval before changing

### Contract You Consume
[Include the lead-authored contract this agent depends on]
- Build against this interface exactly — do not guess or deviate

### Cross-Cutting Concerns You Own
[Explicitly list integration behaviors this agent is responsible for]

## Coordination
- Message the lead if you discover something that affects a contract
- Ask before deviating from any agreed contract
- Flag cross-cutting concerns that weren't anticipated
- Share with [other agent] when: [trigger]
- Challenge [other agent]'s work on: [integration point]

## Before Reporting Done
Run these validations and fix any failures:
1. [specific validation command]
2. [specific validation command]
Do NOT report done until all validations pass.
```

## Step 6: Facilitate Collaboration

All agents are working in parallel. Your job as lead is to keep them aligned and unblock them.

### During Implementation

- Relay messages between agents when they flag contract issues
- If an agent needs to deviate from a contract, evaluate the change, update the contract, and notify all affected agents
- Unblock agents waiting on decisions
- Track progress through the shared task list

### Pre-Completion Contract Verification

Before any agent reports "done", run a contract diff:
- "Backend: what exact curl commands test each endpoint?"
- "Frontend: what exact fetch URLs are you calling with what request bodies?"
- Compare and flag mismatches before integration testing

### Cross-Review
Each agent reviews another's work:
- Frontend reviews Backend API usability
- Backend reviews Database query patterns
- Database reviews Frontend data access patterns

## Collaboration Patterns

**Anti-pattern: Parallel spawn without contracts** (agents diverge)
```
Lead spawns all 3 agents simultaneously without defining interfaces
Each agent builds to their own assumptions
Integration fails on URL mismatches, response shape mismatches ❌
```

**Anti-pattern: Fully sequential spawning** (defeats purpose of agent teams)
```
Lead spawns database agent → waits for contract → spawns backend → waits → spawns frontend
Only one agent works at a time, no parallelism ❌
```

**Anti-pattern: "Tell them to talk"** (they won't reliably)
```
Lead tells backend "share your contract with frontend"
Backend sends contract but frontend already built half the app ❌
```

**Good pattern: Lead-authored contracts, parallel spawn**
```
Lead reads plan → defines all contracts upfront → spawns all agents in parallel with contracts included
All agents build simultaneously to agreed interfaces → minimal integration mismatches ✅
```

**Good pattern: Active collaboration during parallel work**
```
Agent A: "I need to add a field to the response — messaging the lead"
Lead: "Approved. Agent B, the response now includes 'metadata'. Update your fetch."
Agent B: "Got it, updating now"
```

## Task Management

Create a shared task list. Since contracts are defined upfront, agents can start building immediately — no inter-agent blocking for initial implementation work. Only block tasks that genuinely require another agent's output (like integration testing).

```
[ ] Agent A: Build UI components
[ ] Agent B: Implement API endpoints
[ ] Agent C: Build schema and data layer
[ ] Agent A + B + C: Integration testing (blocked by all implementation tasks)
```

Track progress and facilitate communication when agents need to coordinate.

## Common Pitfalls to Prevent

1. **File conflicts**: Two agents editing the same file → Assign clear ownership
2. **Lead over-implementing**: You start coding → Stay in Delegate Mode
3. **Isolated work**: Agents don't talk → Require explicit handoffs via lead relay
4. **Vague boundaries**: "Help with backend" → Specify exact files/responsibilities
5. **Missing dependencies**: Agent B waits on Agent A forever → Track blockers actively
6. **Parallel spawn without contracts**: All agents start simultaneously with no shared interfaces → Integration failures. Define contracts before spawning
7. **Implicit contracts**: "The API returns requests" → Ambiguous. Require exact JSON shapes, URLs with trailing slashes, status codes
8. **Orphaned cross-cutting concerns**: URL conventions, error shapes → Nobody owns them. Explicitly assign to one agent
9. **Guardrail violations**: Agent introduces LangGraph, Celery, Redis, WebSockets → Blocked by CLAUDE.md. Include guardrails in every agent's prompt
10. **OpenAPI drift**: Backend changes endpoints without updating `docs/openapi.yaml` → Frontend breaks. Require OpenAPI sync on every change

## Definition of Done

The build is complete when:
1. All agents report their work is done
2. Each agent has validated their own domain
3. Integration points have been tested
4. Cross-review feedback has been addressed
5. The plan's acceptance criteria are met
6. **Lead agent has run end-to-end validation**

---

## Step 7: Validation

Validation happens at two levels: **agent-level** (each agent validates their domain) and **lead-level** (you validate the integrated system).

### Agent Validation

Before any agent reports "done", they must validate their work. When analyzing the plan, identify what validation each agent should run:

**Backend agent** validates:
- Server starts without errors
- All API endpoints respond correctly (per `docs/openapi.yaml`)
- Tests pass: `cd backend && .venv/bin/python -m pytest -v`
- Phone numbers are masked in responses
- No guardrail violations (no LangGraph, Celery, Redis imports)

**Frontend agent** validates:
- TypeScript compiles: `cd frontend && npx tsc --noEmit`
- Build succeeds: `cd frontend && npm run build`
- Dev server starts
- Components render without console errors
- All fetch calls go through `src/lib/api.ts` (not inline)
- `react-leaflet` only imported inside `LeafletMap.tsx` with dynamic import

When spawning agents, include their validation checklist:

```
## Before Reporting Done

Run these validations and fix any failures:
1. [specific validation command]
2. [specific validation command]
3. [manual check if needed]

Do NOT report done until all validations pass.
```

### Lead Validation (End-to-End)

After ALL agents return control to you, run end-to-end validation yourself. This catches integration issues that individual agents can't see.

**Your validation checklist:**

1. **OpenAPI sync check** — verify `docs/openapi.yaml` matches all implemented endpoints
2. **Backend tests pass** — `cd backend && .venv/bin/python -m pytest -v`
3. **Frontend type-check** — `cd frontend && npx tsc --noEmit`
4. **Can the system start?** — Start both services, no startup errors
5. **Does the happy path work?** — Walk through the primary user flow
6. **Do integrations connect?** — Frontend calls backend correctly, data flows through all layers
7. **Are edge cases handled?** — Empty states, error states, loading states

If validation fails:
- Identify which agent's domain contains the bug
- Re-spawn that agent with the specific issue
- Re-run validation after fix

---

## Execute

Now read the plan at `$ARGUMENTS[0]` and begin:

1. Read and understand the plan
2. Read `CLAUDE.md` for project guardrails
3. Determine team size (use `$ARGUMENTS[1]` if provided, otherwise decide)
4. Define agent roles, ownership, cross-cutting concern assignments, and validation requirements
5. Map the contract chain and define all integration contracts — use `docs/openapi.yaml` as the backbone
6. Enter Delegate Mode (Shift+Tab)
7. Spawn all agents in parallel with contracts and validation checklists included in their prompts
8. Monitor agents, relay messages, mediate contract deviations
9. Run contract diff before integration — compare backend's curl commands vs frontend's fetch URLs
10. When all agents return, run end-to-end validation yourself
11. If validation fails, re-spawn the relevant agent with the specific issue
12. Confirm the build meets the plan's requirements
13. Git commit all changes with a conventional commit message
