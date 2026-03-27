# Demo Advice — A Thriving City Hall

How to present City Hall tools effectively to judges in 3–5 minutes.

---

## Core principle: Show the before and after

The most compelling City Hall demos show a clear contrast between the current experience and your solution. Judges respond to:
- "Here's what a resident faces today" → "Here's what they experience with our tool"
- "Here's how long it takes staff to do this manually" → "Here's how long it takes with our tool"

Never just show the solution. Always anchor it in the problem first.

---

## For Resident Service Navigation tools (Shapes A, B, C)

### Structure your demo like this
1. **The moment of failure (30 seconds):** Show a resident trying to find the right 311 category on rva.gov or in the current RVA311 dropdown. Show them getting lost, picking the wrong category, or giving up. This is the "before."
2. **Your solution in action (90 seconds):** Show your tool. The resident describes their problem in plain language. The tool routes them correctly. They click the link to submit the official request.
3. **What happened vs. what would have happened (30 seconds):** "Without this tool, this request would have been miscategorized. Staff would have had to manually re-route it. With our tool, it gets to the right department the first time."
4. **Evidence of reliability (30 seconds):** Show that your tool acknowledges uncertainty. "If we're not confident, we say so and direct to 311 staff." This builds credibility.

### What judges look for
- Real routing logic — did you actually map to the correct category?
- Human fallback — does your tool tell users to call 311 if it's uncertain?
- Source transparency — where does the information come from?
- Honesty about limitations — does it overclaim?

### Red flags judges notice
- A tool that confidently routes any query, no matter how ambiguous
- No link to official RVA311 for actual submission
- Claims to "integrate with" or "connect to" the City's RVA311 system (you can't)
- Routing suggestions that are clearly wrong for the scenario

---

## For Procurement tools (Shapes C, D, E)

### Structure your demo like this
1. **The current pain (30 seconds):** "A procurement officer needs to find all contracts expiring in the next 60 days. Right now, they download the CSV, open it in Excel, manually sort by date, and check each contract PDF. This takes [X] hours per cycle."
2. **Your solution in action (90 seconds):** Show the dashboard loading. Apply the "expiring in 60 days" filter. Show 8 contracts. Click one to see the key details. If you have PDF extraction: upload a sample contract and show the extracted summary in 10 seconds.
3. **The decision this enables (30 seconds):** "Now the procurement officer can see in one view what needs attention. They can prioritize their PDF review. They don't miss renewal windows."
4. **What you're not claiming (30 seconds):** "This is a decision-support tool, not a compliance system. Staff still make the final determination. We surface the information; they act on it."

### What judges look for
- Real data — did you use the actual City Contracts dataset?
- Practical value — does it actually save time?
- Appropriate scope — does it support staff judgment rather than replace it?
- Honesty about the "advisory only" nature of the tool

### Red flags judges notice
- Claims to make compliance determinations or contracting decisions
- Using synthetic or fake contract data when real public data exists
- PDF extraction that works perfectly on one document but would clearly fail on others
- No disclaimer about the AI-assisted nature of extraction

---

## General demo logistics

### Technical setup
- Test your demo environment at least 30 minutes before judging
- Have a backup: screenshots or a recorded demo in case of live failure
- If your tool requires live API calls, test the API before the demo starts
- Pre-load any data that takes time to process

### Timing
- 3–5 minutes total is typical; practice to hit the sweet spot
- Spend 1 minute on problem, 2 minutes on solution, 1 minute on credibility/limitations/next steps
- Leave 30 seconds for a clear closing ask or "what we'd need to take this further"

### Framing language that works
- "This helps [specific user] do [specific task] instead of [current painful approach]"
- "We used the City's public contract data — here's the source"
- "If the tool isn't certain, it says so and points to staff"
- "This is a decision-support tool — the human still makes the final call"

### Framing language to avoid
- "This automates City procurement" or "this replaces 311"
- "This integrates with the City's systems" (unless you actually do, with permission)
- "This will save millions of dollars" (you don't know that yet)
- "This is ready to deploy" (it's a prototype)
