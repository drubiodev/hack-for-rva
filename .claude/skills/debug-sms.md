---
description: Debug the SMS conversation pipeline — Twilio webhook delivery, session state machine, AI classification, and database writes
---

Debug an issue in the HackathonRVA 311 SMS conversation flow. Work through the pipeline systematically based on the observed symptom.

---

## Pipeline overview

```
Citizen SMS
    ↓
Twilio (toll-free number)
    ↓ POST /webhooks/sms
    │   form fields: From (E.164 phone), Body, MessageSid
FastAPI: sms/router.py
    ↓ validate Twilio signature (X-Twilio-Signature header)
    ↓ lookup sessions[phone]
    │
    ├── No session found
    │   └── ai/classifier.py: classifier.ainvoke(body) → ServiceRequest311
    │       sessions[phone] = {"step": "confirm", "data": {...}}
    │       return: "Got it: {category} at {location}. Reply YES to confirm."
    │
    └── Session exists, step == "confirm"
        ├── body contains "yes" → BackgroundTasks: save_to_db(data)
        │                          del sessions[phone]
        │                          return: "Submitted! Reference #..."
        └── body does not contain "yes" → del sessions[phone]
                                           return: "Cancelled."
    ↓
TwiML XML → Twilio → SMS reply to citizen
    ↓ (background task)
PostgreSQL via asyncpg → service_requests table
```

---

## Diagnose by symptom

### Symptom A: No SMS reply received at all

**Step 1 — Check Twilio delivery logs:**
- Twilio Console → Monitor → Logs → Messaging
- Find the inbound message — did Twilio fire a webhook to your Railway URL?
- What HTTP status code did your backend return?
  - 200 → backend processed it but TwiML was empty → check Step 3
  - 4xx/5xx → backend errored → check Railway logs immediately
  - Timeout / connection refused → Railway service is down or webhook URL is wrong

**Step 2 — Check Railway logs:**
- Railway dashboard → backend service → Logs
- Look for Python exceptions during the request window
- Look for: "Invalid Twilio signature" (would explain silent reject)
- Look for: `pydantic_settings` errors (missing env var on startup)

**Step 3 — Verify webhook URL in Twilio:**
- Must be `https://` not `http://`
- No trailing slash issues
- Test directly:
  ```bash
  curl -X POST https://YOUR-BACKEND.up.railway.app/webhooks/sms \
    -d "From=%2B18045550100&Body=test+pothole&MessageSid=SMtest001"
  ```
  Should return TwiML XML starting with `<?xml` or `<Response>`

---

### Symptom B: Reply received but request not appearing in the dashboard

**Step 1 — Did the user reply YES?**
The conversation requires a YES confirmation. If the citizen texted the report but didn't reply YES, the request is still in `sessions` state and hasn't been written to the database.

**Step 2 — Check the database directly:**
```bash
curl https://YOUR-BACKEND.up.railway.app/api/v1/requests?limit=5
```
If the request is in the API response but not in the dashboard → frontend polling issue (see below).
If the request is NOT in the API response → database write issue.

**Step 3 — Check BackgroundTask execution:**

Add temporary logging to verify the background task runs:
```python
# app/sms/service.py
import logging
logger = logging.getLogger(__name__)

async def save_to_db(data: dict, db_session):
    logger.info("save_to_db called: category=%s location=%s", data.get("category"), data.get("location"))
    # ... existing code ...
    logger.info("save_to_db complete: id=%d", new_request.id)
```

**Step 4 — Check frontend polling:**
- Browser DevTools → Network tab → filter by `/api/v1/requests`
- Requests should appear every 30 seconds
- If no requests visible → `NEXT_PUBLIC_API_URL` may be wrong or missing
- If requests fail with CORS error → backend `FRONTEND_URL` env var needs updating

---

### Symptom C: Wrong AI classification (wrong category, missing location)

**Step 1 — Test the classifier in isolation:**
```python
# Run from backend/ directory
import asyncio
from app.ai.classifier import classifier

async def test_classify(text: str):
    result = await classifier.ainvoke(text)
    print(f"category={result.category} location={result.location} urgency={result.urgency} confidence={result.confidence}")

asyncio.run(test_classify("There's graffiti on the bridge on 9th street near the canal"))
```

**Step 2 — Check Azure deployment names:**
- `AZURE_DEPLOYMENT_CLASSIFIER` must be `gpt-41-nano` (matches the Azure deployment name — note: no dot in the deployment name)
- Verify in Azure OpenAI Studio → Deployments → confirm the exact deployment name string

**Step 3 — Review the system prompt:**
```python
# app/ai/prompts.py — check the category list is complete:
# pothole, streetlight, graffiti, trash, water, sidewalk, noise, other
# Check the field descriptions in ServiceRequest311 in app/ai/classifier.py
```

**Step 4 — Low confidence score:**
If `confidence < 0.7`, the input is ambiguous. Options:
- Add a clarification step: "I classified this as {category}. Is that right? Reply YES or type a correction."
- Adjust the system prompt to give more examples for the ambiguous categories

---

### Symptom D: Conversation stuck — second message starts a new report instead of confirming

**Cause:** Session not found on the second message. Session key is the `From` phone number.

**Step 1 — Check phone number format consistency:**
All Twilio messages should arrive in E.164 format (`+18045550100`). Verify the `From` field is consistent between messages.

**Step 2 — Check if backend restarted between messages:**
The `sessions` dict is in-memory — it's lost on any backend restart. Railway restarts on each new deployment.

**Solution for demo:** Add a `/debug/sessions` endpoint temporarily:
```python
# app/api/router.py — REMOVE BEFORE DEMO
@router.get("/debug/sessions", include_in_schema=False)
async def debug_sessions():
    from app.sms.service import sessions
    # Redact phone numbers in output
    return {f"...{k[-4:]}": v for k, v in sessions.items()}
```

---

### Symptom E: "Invalid Twilio signature" in Railway logs

**Cause:** The URL passed to `RequestValidator.validate()` doesn't exactly match what Twilio sent.

**Most common cause on Railway:** Railway terminates HTTPS and forwards requests as HTTP internally. The URL seen by FastAPI is `http://...` but Twilio signed `https://...`.

**Fix:**
```python
# app/sms/router.py
proto = request.headers.get("X-Forwarded-Proto", "https")
url = str(request.url).replace("http://", f"{proto}://", 1)
# Use this `url` in validator.validate(), not str(request.url)
```

**Also verify:**
- `TWILIO_AUTH_TOKEN` is the **auth token**, not the account SID (they look similar)
- The webhook URL in Twilio Console exactly matches your Railway URL (no trailing slash, correct subdomain)

---

## Quick diagnostic commands

```bash
BACKEND=https://your-backend.up.railway.app

# Health check
curl -s $BACKEND/health

# Current requests in DB
curl -s "$BACKEND/api/v1/requests?limit=3" | python3 -m json.tool

# Simulate inbound SMS (no Twilio signature — will fail validation but show if app is running)
curl -X POST $BACKEND/webhooks/sms \
  -d "From=%2B18045550100&Body=pothole+on+Broad+Street&MessageSid=SMtest"

# Check active sessions (only if debug endpoint is enabled)
curl -s $BACKEND/debug/sessions
```

---

## When called

If the user describes a specific symptom, go directly to that section. If no symptom is given:
1. Run `git log --oneline -5` to see recent changes that may have introduced the issue
2. Read `backend/app/sms/service.py` and `backend/app/sms/router.py`
3. Ask: "What are you seeing?" and list the four symptoms above as options
4. Walk through the relevant diagnostic checklist

Give specific commands to run — not generic "check your logs" advice.
