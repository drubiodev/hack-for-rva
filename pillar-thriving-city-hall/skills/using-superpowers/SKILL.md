# using-superpowers

Purpose: Establish the skill-check protocol — run before every response.

## When To Use
- At the start of every conversation.
- Before any response, including clarifying questions.
- Whenever you are about to improvise instead of using a skill.

## The Rule

Before responding to any user message, ask: **does a skill in `skills/` apply to this task?**

If there is even a 1% chance a skill applies, read that skill's `SKILL.md` and follow it. Do not respond first and check later.

## Decision Flow

1. User message received
2. Ask: does any skill in `skills/` apply?
3. If yes → read `skills/<name>/SKILL.md`, announce "Using [skill] to [purpose]", follow exactly
4. If no → respond directly

## Skill Priority

1. **Process skills first** — `repo_memory`, `problem_scoping`, `research_corpus_navigation`
2. **Implementation skills second** — `mvp_designer`, `risk_review`, `demo_coach`, `dataset_mapper`

## Red Flags (Stop — You Are Rationalizing)

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |

## How to Invoke a Skill

1. Read the file: `skills/<name>/SKILL.md`
2. Announce: "Using [skill name] to [purpose]"
3. Follow the skill exactly

## Non-negotiable

Hackbot prefers executing skills over improvising. This is not optional.
