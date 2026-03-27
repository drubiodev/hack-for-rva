# Risk Review Prompt — A Thriving City Hall

Use this prompt before finalizing your demo script, product copy, or any public-facing claims.

---

## When to use this

- Before sharing product copy or UI text with judges
- Before demoing any routing or service recommendation
- When your tool makes any claim about what a resident should do or what a contract says
- Before claiming integration with any City system

---

## Prompt to run

```
I am building a civic tech prototype for the A Thriving City Hall pillar at the Richmond Civic Hackathon.

My prototype:
[FILL IN: describe what your tool does — e.g., "A 311 category helper that takes a plain-language description and returns the recommended RVA311 request type with a link to the official portal"]

The tool's current copy/claims:
[FILL IN: paste the key UI text, demo script, or claims you want reviewed]

Please review this for the following risks specific to City Hall civic tech:

1. WRONG ROUTING HARM: Does the tool confidently route residents to the wrong service? What happens if the recommendation is wrong? Does the tool acknowledge uncertainty and provide a human fallback (e.g., "call 311" or "contact [department]")?

2. HALLUCINATED SERVICES: Does the tool invent City programs, services, or departments that may not exist or may have changed?

3. OFFICIAL AUTHORITY CLAIM: Does the tool imply it is an official City interface, that submissions are being made on behalf of the user, or that its answers represent the City's official position?

4. LEGAL/COMPLIANCE CLAIM: For procurement tools — does the tool claim to determine legal compliance, contract validity, or award eligibility?

5. DATA STALENESS: Does the tool use rva.gov content that may be outdated? Does it show a "last verified" date or source link for each piece of information?

6. RVA311 API CLAIM: Does the tool claim to pull live 311 data or "connect to" the AvePoint/Dynamics 365 system? (This is not possible — there is no public API.)

7. INCLUSION RISK: Is the tool accessible to residents with lower digital literacy, on mobile devices, or who need translation support?

For each risk found, suggest:
- A specific rewrite of the problematic text
- A disclaimer or disclaimer placement
- Whether the feature should be scoped out entirely
```

---

## City Hall-specific red lines (non-negotiable)

These claims must be removed or corrected regardless of how well the tool works:
- Any claim that a submission was made to the City through your tool (unless you have explicit City authorization)
- Any claim that your routing recommendation is official or authoritative
- Any claim to have real-time or live RVA311 data (the post-2018 API does not exist)
- Any claim that a contract is legally compliant based on your tool's analysis
- Any implication that your tool replaces calling 311 or speaking to a procurement officer

---

## What to do with the output

1. Address each flagged risk with a specific fix
2. Add disclaimers where needed
3. Update your demo script to include the human fallback moment
4. Log the review in `evidence_log.md` with date and status
