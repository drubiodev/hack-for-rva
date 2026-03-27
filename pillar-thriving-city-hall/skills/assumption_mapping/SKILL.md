# assumption_mapping

Purpose: Identify and prioritize risky assumptions to test before building.

## When To Use
- Solution has many unknowns
- Need to de-risk quickly
- Before committing to an MVP

## Inputs
- Proposed solution

## Process
1. List all assumptions embedded in the solution
2. Score each assumption on two axes:
   - **Risk** — how bad is it if this assumption is wrong?
   - **Uncertainty** — how confident are you it is true?
3. Plot on 2x2 grid:
   - High risk + high uncertainty → test first
   - High risk + low uncertainty → monitor
   - Low risk + high uncertainty → accept or defer
   - Low risk + low uncertainty → ignore
4. Define a validation approach for each top assumption

## Outputs
- Assumption map (2x2 grid)
- Top risks to validate
- Test plan for each high-priority assumption

## Constraints
- Do not ignore high-risk assumptions
- Avoid spending time validating low-impact items first
