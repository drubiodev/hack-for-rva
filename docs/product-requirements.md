# 311 SMS Civic Service — Product Requirements Document

**Project:** HackathonRVA 2026 — 311 SMS Civic Service
**Team:** Priyesh (Backend) + Daniel (Frontend)
**Timeline:** 48 hours | **Budget:** ~$65
**Date:** March 26, 2026

---

## 1. Executive Summary

Richmond residents currently navigate clunky web forms and phone trees to report potholes, broken streetlights, and other civic issues — a process that discourages reporting and leaves problems unfixed. We built a zero-friction SMS-based 311 system where any resident can text a plain-English report to a single number, AI instantly classifies and confirms it, and city operations staff see every report on a live dashboard with map visualization and analytics. No app to download, no form to fill out, no smartphone required — just text and go.

---

## 2. OKRs

### Objective 1: Demonstrate a working end-to-end civic tech loop

| Key Result | Target | Measurement |
|---|---|---|
| KR1: Citizen texts a report and receives AI confirmation SMS | < 10 seconds end-to-end | Timer during live demo |
| KR2: Confirmed report appears on dashboard without manual reload | < 30 seconds | Visual observation on dashboard |
| KR3: Correct AI classification across core service categories during demo | >= 5 of 8 categories | Pre-scripted test message set |

### Objective 2: Show AI-powered intelligence, not just CRUD

| Key Result | Target | Measurement |
|---|---|---|
| KR1: AI classification accuracy across the 8 core categories | >= 90% | Manual check of 10 scripted test messages |
| KR2: Urgency scoring visibly affects dashboard priority ordering | Visible in demo | Judge observation of sorted request list |
| KR3: AI confidence scores displayed on request cards | Present in UI | Dashboard screenshot |

### Objective 3: Deliver a production-credible operations experience

| Key Result | Target | Measurement |
|---|---|---|
| KR1: Map shows geographically distributed requests with category differentiation | Color-coded pins on Richmond map | Live map view during demo |
| KR2: Dashboard auto-refreshes without manual page reload | Every 30 seconds via polling | Visual observation |
| KR3: Status workflow (new -> open -> in_progress -> resolved) is demonstrable in real time | Full lifecycle in < 2 minutes | Live demo walkthrough |

---

## 3. KPI Table

| KPI | Target | Measurement Method | Owner |
|---|---|---|---|
| SMS response latency | < 10 seconds | Timer during live demo; backend logging | Priyesh |
| AI classification accuracy | >= 90% (9/10 correct) | Pre-scripted 10-message test suite | Priyesh |
| Dashboard data refresh lag | <= 30 seconds | Visual observation of new report appearance | Daniel |
| Category coverage | 8 of 8 categories classifiable | One test message per category | Priyesh |
| System uptime during demo | 100% | Railway health check before presenting | Both |
| Map pin accuracy | Pins appear in correct Richmond area | Visual verification against known addresses | Daniel |
| End-to-end flow completion | SMS -> classify -> confirm -> dashboard in < 60s | Timed full-flow test | Both |
| Total infrastructure cost | <= $65 | Twilio + Railway billing dashboards | Priyesh |

---

## 4. User Stories

### Citizen (SMS User)

| ID | Story | Acceptance Criteria |
|---|---|---|
| C-1 | As a Richmond resident, I want to text a description of a civic issue so that I can report it without downloading an app or visiting a website. | SMS to toll-free number is received and processed; AI sends classification confirmation within 10 seconds. |
| C-2 | As a citizen, I want the system to confirm what it understood before submitting so that I know my report is accurate. | System replies with extracted category, location, and description; asks "Reply YES to confirm." |
| C-3 | As a citizen, I want to receive a reference number after confirmation so that I can track my report. | After replying YES, citizen receives "Submitted! Reference #XXXXX." |
| C-4 | As a citizen, I want to cancel a report if the AI misunderstood so that incorrect reports are not submitted. | Any reply other than YES cancels the report; citizen receives "Cancelled. Text us anytime." |
| C-5 | As a citizen, I want to report issues in plain English so that I don't need to know category codes or fill structured fields. | Free-text messages like "huge pothole on 5th and Main" are correctly parsed into category + location + urgency. |

### City Staff (Dashboard User)

| ID | Story | Acceptance Criteria |
|---|---|---|
| S-1 | As a city operations manager, I want to see all incoming reports in a sortable list so that I can triage and prioritize work. | Dashboard shows request list with columns: category, location, status, priority, timestamp; sortable and filterable. |
| S-2 | As a city staff member, I want to view reports on a map so that I can identify geographic clusters and dispatch crews efficiently. | Map view shows pins at report locations, color-coded by category, with popup details on click. |
| S-3 | As a city staff member, I want to update the status of a request so that I can track progress from new to resolved. | Status dropdown on request detail page; changes to new/open/in_progress/resolved persist and reflect in the list. |
| S-4 | As a city operations manager, I want to see KPI summary cards so that I have an at-a-glance view of system activity. | Dashboard overview shows total requests, requests by status, and requests by category as summary cards. |
| S-5 | As a city analyst, I want to see category breakdown charts so that I can identify the most common types of issues being reported. | Analytics page shows bar chart of request counts by category. |
| S-6 | As a city staff member, I want the dashboard to auto-refresh so that I see new reports without manually reloading the page. | Dashboard updates every 30 seconds via TanStack Query polling; no manual refresh needed. |

---

## 5. MoSCoW Feature Matrix

### Must Have — Demo fails without these

| Feature | Owner | Est. Hours | Rationale |
|---|---|---|---|
| Twilio SMS receive + TwiML response within 10s | Priyesh | 3 | Core input channel; no SMS = no demo |
| AI classification with structured output (category, location, urgency, confidence) | Priyesh | 5 | The "AI" in our pitch; judges expect intelligence |
| Confirmation flow: report -> "Reply YES to confirm" -> saved to DB | Priyesh | 3 | Demonstrates human-in-the-loop AI; prevents garbage data |
| REST API: `GET /api/v1/requests` serving real data | Priyesh | 2 | Frontend depends on this endpoint from hour 10+ |
| Dashboard request list with status and category badges | Daniel | 4 | Primary operations view |
| Map view with request pins on Richmond map | Daniel | 3 | Geographic context is the visual wow-factor |
| Both services deployed and live on Railway | Both | 2 | "It works on my machine" doesn't win hackathons |

### Should Have — Impresses judges

| Feature | Owner | Est. Hours | Rationale |
|---|---|---|---|
| Dashboard auto-refresh (30s TanStack Query polling) | Daniel | 1 | "Real-time" feel; one config line in TanStack Query |
| KPI summary cards (total requests, by status, by category) | Daniel | 2 | At-a-glance operational intelligence |
| Priority/urgency visual differentiation on request list | Daniel | 1 | Shows AI urgency scoring has downstream impact |
| Request detail view with conversation history | Daniel | 2 | Proves multi-turn SMS flow exists |
| Category breakdown bar chart (analytics page) | Daniel | 2 | Data visualization impresses judges |
| `PATCH /api/v1/requests/:id` for status updates | Priyesh | 1 | Enables staff workflow demo |

### Could Have — Stretch goals if time allows

| Feature | Owner | Est. Hours | Rationale |
|---|---|---|---|
| Geocoding: convert address text to lat/lng for accurate map pins | Priyesh | 2 | More accurate map; requires external API |
| RAG with FAISS for similar-request detection | Priyesh | 4 | "3 other potholes reported nearby" — impressive but time-heavy |
| Request clustering on the map | Daniel | 3 | Visual pattern detection |
| SMS status updates when a request is resolved | Priyesh | 2 | Closes the citizen feedback loop |
| Dark mode toggle | Daniel | 1 | Polish |
| Mobile-responsive dashboard | Daniel | 2 | Shows production readiness |

### Won't Have — Explicitly out of scope

| Feature | Reason |
|---|---|
| Authentication / login | 4+ hours of work; judges won't notice its absence |
| LangGraph or complex AI orchestration | 80-line state machine covers the demo; LangGraph adds no visible value |
| Redis or Celery | PostgreSQL and in-memory state handle hackathon scale trivially |
| WebSockets or SSE | 30s polling is indistinguishable from real-time for the demo |
| A2P 10DLC registration | 10-15 business day process; toll-free number works immediately |
| Image-based reports (MMS) | Interesting but doubles AI complexity for minimal demo impact |
| Multi-language support | English-only for the hackathon |

---

## 6. Demo Narrative

### Opening Hook (30 seconds)

> "Right now in Richmond, if you see a pothole, you have to find a website, fill out a form, and hope someone reads it. We built a better way — any phone, any carrier, no app needed. Just text."

### Live Demo Script (4-5 minutes)

**Step 1 — Citizen reports an issue (60 seconds)**

- Pick up phone on stage. Text: *"There's a broken streetlight at 5th and Main, been out for a week"* to the demo number.
- Show the phone screen to the audience/judges.
- Wait for the AI reply (~5 seconds): *"Got it: streetlight at 5th and Main. Reply YES to confirm."*
- Reply YES. Receive confirmation: *"Submitted! Reference #12345."*

**Step 2 — Dashboard shows the report (30 seconds)**

- Switch to the laptop showing the dashboard.
- Point out the new request appearing in the request list within 30 seconds.
- Highlight the AI-assigned category badge ("streetlight"), urgency level, and confidence score.

**Step 3 — Map view (30 seconds)**

- Navigate to the map view.
- Show the new pin on the Richmond map alongside pre-seeded sample data.
- Click a pin to show the popup with report details.
- Point out geographic clustering: "City staff can immediately see which neighborhoods need attention."

**Step 4 — Staff workflow (30 seconds)**

- Click into a request detail view.
- Change status from "new" to "in_progress."
- Return to the list view — show the status badge has updated.
- "City staff can triage and track every report through resolution."

**Step 5 — Analytics (30 seconds)**

- Navigate to the analytics page.
- Show category breakdown chart: "Potholes are 40% of all reports — the city now has data to prioritize road repair budgets."
- Show KPI cards: total reports, open vs. resolved, average response time.

**Step 6 — Second live text (30 seconds)**

- Text another report from a different phone (or the same phone): *"Graffiti on the underpass at Broad and Belvidere, really offensive"*
- Show the AI correctly classifying it as "graffiti" with "high" urgency.
- Confirm and watch it appear on the dashboard and map in real time.

### Closing (30 seconds)

> "We built this in 48 hours for $65. The SMS gateway, AI classification, operations dashboard, and map view are all live right now. No app to download, no form to fill out — Richmond residents can report issues from any phone, and city staff get instant visibility. This is what civic tech should be: simple, accessible, and intelligent."

### Key Differentiators to Highlight if Judges Ask

- **Zero friction:** Works on any phone — flip phones, smartphones, no data plan needed.
- **AI-powered:** Natural language in, structured data out. No category codes or dropdown menus.
- **Real-time operations:** City staff see reports the moment they're confirmed.
- **Cost-effective:** ~$65 total infrastructure cost for a production-viable system.
- **Scalable architecture:** Same system handles 100 or 100,000 reports with minimal changes.

---

## 7. Success Criteria

The project is "done" for the hackathon when all of the following are true:

| # | Criterion | Verification |
|---|---|---|
| 1 | A text message to the Twilio number triggers an AI-classified confirmation reply within 10 seconds. | Live test on stage. |
| 2 | Replying YES saves the report to Supabase and it appears on the dashboard within 30 seconds. | Visual confirmation on dashboard. |
| 3 | The dashboard request list displays category, location, status, priority, and timestamp for all reports. | Judge inspection. |
| 4 | The map view shows report pins on a Richmond, VA map with category differentiation. | Visual confirmation. |
| 5 | At least 5 of 8 categories are correctly classified by the AI during the live demo. | Pre-scripted test messages. |
| 6 | Both backend and frontend are deployed and accessible via public Railway URLs. | URLs load in browser. |
| 7 | The full SMS -> dashboard -> map flow completes without errors during the judge demo. | Successful live demo. |
| 8 | Total infrastructure spend is under $65. | Billing dashboard screenshots. |

---

## 8. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Twilio toll-free verification is delayed beyond the hackathon window | Medium | High | Fall back to Twilio trial account with pre-verified judge phone numbers. Trial prefix is cosmetic only. |
| 2 | Azure OpenAI API is slow or rate-limited | Low | High | Pre-warm the deployment; have a hardcoded classification fallback for the demo (switch statement on keywords). |
| 3 | Railway deployment fails or has cold-start latency | Low | Medium | Test deployment by hour 2; keep local `docker-compose` as backup for live demo from laptop. |
| 4 | AI misclassifies reports during live demo | Medium | High | Use pre-tested demo scripts with known-good classifications. Practice the exact demo texts 5+ times before presenting. |
| 5 | Supabase free tier connection limits hit | Low | Low | Free tier allows 60 connections; hackathon load won't exceed 5. Not a real risk but monitor. |
| 6 | Cross-team integration delay (API contract mismatch) | Medium | High | Agree on exact JSON response shape in hour 0; Priyesh provides mock endpoint by hour 4, real data by hour 10. |
| 7 | React-Leaflet SSR crash on Next.js | Medium | Medium | Use `dynamic()` import with `ssr: false`. Known pattern, documented in architecture plan. |
| 8 | Scope creep — trying to build stretch goals before Must Haves are solid | High | High | Enforce MoSCoW strictly. No Could Have work until all Must Haves are demo-tested end-to-end. |
| 9 | Sleep deprivation causes bugs in final hours | High | Medium | Plan the final 8 hours for polish and demo prep only — no new features after hour 40. |
| 10 | Demo phone has no signal in the venue | Low | High | Test venue cell coverage on arrival; have a backup phone on a different carrier. Use venue WiFi + Twilio API as fallback for triggering inbound messages. |

---

## 9. 48-Hour Sprint Plan

### Hour 0-2: Foundation (Both)

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 0:00 | Agree on API contract: `GET /api/v1/requests` JSON shape | Agree on API contract: `GET /api/v1/requests` JSON shape |
| 0:30 | Scaffold FastAPI app, config, Supabase connection | Scaffold Next.js 16 + shadcn/ui + TanStack Query |
| 1:00 | Create database tables via `create_all()` | Install shadcn components: sidebar, table, card, badge, tabs |
| 1:30 | Deploy skeleton backend to Railway | Deploy skeleton frontend to Railway |
| 2:00 | **Checkpoint: Both services live on Railway with health endpoints** | **Checkpoint: Both services live on Railway with health endpoints** |

### Hour 2-6: Core Input Channel (Priyesh) + Layout (Daniel)

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 2-3 | Twilio webhook endpoint, signature validation | Dashboard layout with shadcn Sidebar navigation |
| 3-4 | Basic TwiML echo response (prove SMS works) | KPI summary cards (hardcoded data) |
| 4-5 | Azure OpenAI integration, structured output classifier | Overview page layout with placeholder data |
| 5-6 | Test: text a message, get AI classification back via SMS | Mock API data for request list development |
| 6:00 | **Checkpoint: SMS -> AI classification -> reply works end-to-end** | **Checkpoint: Dashboard layout and navigation complete** |

### Hour 6-12: AI Pipeline (Priyesh) + Data Views (Daniel)

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 6-8 | Confirmation flow: "Reply YES" state machine | DataTable for request list (TanStack Table + shadcn) |
| 8-10 | `GET /api/v1/requests` endpoint with real DB data | Sorting, filtering, category/status badges on list |
| 10-12 | `PATCH /api/v1/requests/:id` for status updates | Connect to real API (Priyesh's endpoint is live by hour 10) |
| 12:00 | **Checkpoint: Full SMS flow works; API serves real data** | **Checkpoint: Request list shows real data from API** |

### Hour 12-18: Integration + Map (Critical)

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 12-14 | Analytics endpoints (counts by category, status, time) | Map view with React-Leaflet (dynamic import, OSM tiles) |
| 14-16 | Edge case handling: invalid messages, duplicate reports | Request pins on map with category colors and popups |
| 16-18 | Seed database with 20-30 realistic Richmond reports | Request detail page with conversation history |
| 18:00 | **Checkpoint: Map view works with real pins; 20+ seeded reports** | **Checkpoint: Map view works with real pins; detail page done** |

### Hour 18-24: Should-Have Features

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 18-20 | Reference number generation, response message polish | TanStack Query auto-polling (30s refetchInterval) |
| 20-22 | Error handling, logging, input sanitization | Analytics page: category breakdown bar chart |
| 22-24 | Load test: send 50 SMS messages, verify pipeline | KPI cards connected to real analytics endpoints |
| 24:00 | **Checkpoint: All Must Haves and most Should Haves complete** | **Checkpoint: All Must Haves and most Should Haves complete** |

### Hour 24-32: Polish + Stretch Goals

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 24-28 | Geocoding integration (if time) or hardcode Richmond coords | Priority/urgency visual differentiation |
| 28-32 | RAG with FAISS for similar requests (stretch) | Mobile responsiveness, loading states, empty states |
| 32:00 | **Checkpoint: Stretch goals attempted; system stable** | **Checkpoint: UI polished; responsive on mobile** |

### Hour 32-40: Hardening + Demo Prep

| Time | Priyesh (Backend) | Daniel (Frontend) |
|---|---|---|
| 32-36 | End-to-end integration testing (10 scripted SMS tests) | Dark mode toggle (if time) |
| 36-40 | Fix any bugs found in testing; freeze backend code | Fix any UI bugs; freeze frontend code |
| 40:00 | **Checkpoint: Code freeze. No new features after this point.** | **Checkpoint: Code freeze. No new features after this point.** |

### Hour 40-48: Demo Rehearsal + Presentation

| Time | Both |
|---|---|
| 40-42 | Full demo rehearsal #1: run the complete demo script end-to-end |
| 42-43 | Fix any issues discovered during rehearsal |
| 43-45 | Full demo rehearsal #2: practice timing, transitions, talking points |
| 45-46 | Final system check: Railway health, Twilio balance, database state |
| 46-47 | Seed fresh demo data, clear test data, prepare demo phones |
| 47-48 | Final rehearsal #3, relax, present |
| 48:00 | **Demo time.** |

### Sprint Rules

1. **No new features after hour 40.** The final 8 hours are for testing, fixing, and rehearsing only.
2. **MoSCoW is law.** No Could Have work begins until every Must Have is demo-tested.
3. **Deploy early, deploy often.** Push to Railway after every working feature. Never accumulate more than 2 hours of undeployed code.
4. **The demo is the product.** If it doesn't show well on stage, it doesn't matter how elegant the code is.
5. **Communicate blockers immediately.** If either team member is stuck for more than 30 minutes, say something.
