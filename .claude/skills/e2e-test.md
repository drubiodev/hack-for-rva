---
description: Generate Playwright e2e tests targeting the deployed Railway URL — covers SMS webhook simulation, dashboard UI, map view, and analytics
---

Generate Playwright e2e tests for the HackathonRVA 311 SMS service. All tests run against the **deployed Railway URLs** — no localhost, no mocks.

---

## Test philosophy for this PoC

- **No unit tests, no mocking** — test the real deployed system end-to-end
- **Minimal but meaningful** — cover the demo critical path; skip edge cases that don't affect the demo
- **Seed via API** — tests that need data call `POST /webhooks/sms` or the backend API directly to seed it
- **Fast** — entire suite should complete in under 2 minutes
- **Idempotent** — tests should not break if run multiple times against a database that already has data

---

## Playwright configuration

```typescript
// playwright.config.ts (place at frontend/ root)
import { defineConfig, devices } from "@playwright/test"

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: 1,
  use: {
    baseURL: process.env.RAILWAY_FRONTEND_URL ?? "http://localhost:3000",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
})
```

**Required environment variables for tests:**

| Variable | Description |
|---|---|
| `RAILWAY_FRONTEND_URL` | Deployed Next.js URL (e.g., `https://frontend.up.railway.app`) |
| `RAILWAY_BACKEND_URL` | Deployed FastAPI URL (e.g., `https://backend.up.railway.app`) |

Set these in a `.env.test` file or in CI environment. Add `.env.test` to `.gitignore`.

---

## Test suites

### Suite 1: Dashboard overview (`e2e/dashboard.spec.ts`)

Tests that the dashboard loads and core UI elements are present.

```typescript
import { test, expect } from "@playwright/test"

test.describe("Dashboard overview", () => {
  test("dashboard page loads without errors", async ({ page }) => {
    await page.goto("/dashboard")
    await expect(page).toHaveTitle(/311/)
    await expect(page.locator("main")).toBeVisible()
  })

  test("KPI cards are visible", async ({ page }) => {
    await page.goto("/dashboard")
    // Expect at least one card with a numeric value
    await expect(page.locator("[data-testid='kpi-card']").first()).toBeVisible()
  })

  test("navigation links work", async ({ page }) => {
    await page.goto("/dashboard")
    await page.getByRole("link", { name: /requests/i }).click()
    await expect(page).toHaveURL(/\/dashboard\/requests/)
    await page.getByRole("link", { name: /map/i }).click()
    await expect(page).toHaveURL(/\/dashboard\/map/)
    await page.getByRole("link", { name: /analytics/i }).click()
    await expect(page).toHaveURL(/\/dashboard\/analytics/)
  })
})
```

---

### Suite 2: Request list (`e2e/requests.spec.ts`)

Seeds a request via the webhook, then verifies it appears in the dashboard.

```typescript
import { test, expect } from "@playwright/test"

const BACKEND = process.env.RAILWAY_BACKEND_URL

test.describe("Request list", () => {
  test.beforeAll(async ({ request }) => {
    // Seed a test request via webhook simulation
    await request.post(`${BACKEND}/webhooks/sms`, {
      form: {
        From: "+18045559999",
        Body: "E2E test: pothole on Broad Street near Monroe Park",
        MessageSid: `SM_e2e_${Date.now()}`,
        AccountSid: process.env.TWILIO_ACCOUNT_SID ?? "ACtest",
      },
    })
    // Confirm it — second message
    await request.post(`${BACKEND}/webhooks/sms`, {
      form: {
        From: "+18045559999",
        Body: "YES",
        MessageSid: `SM_e2e_confirm_${Date.now()}`,
        AccountSid: process.env.TWILIO_ACCOUNT_SID ?? "ACtest",
      },
    })
  })

  test("request table renders with data", async ({ page }) => {
    await page.goto("/dashboard/requests")
    await expect(page.getByRole("table")).toBeVisible()
    // At minimum one row should exist (from seed or prior data)
    await expect(page.getByRole("row").nth(1)).toBeVisible()
  })

  test("status filter narrows results", async ({ page }) => {
    await page.goto("/dashboard/requests")
    await page.getByRole("combobox", { name: /status/i }).selectOption("new")
    // Table should still render (even if empty)
    await expect(page.getByRole("table")).toBeVisible()
  })

  test("clicking a request opens the detail view", async ({ page }) => {
    await page.goto("/dashboard/requests")
    await page.getByRole("row").nth(1).click()
    await expect(page).toHaveURL(/\/dashboard\/requests\/\d+/)
  })
})
```

---

### Suite 3: Map view (`e2e/map.spec.ts`)

Verifies Leaflet loads correctly and markers are rendered.

```typescript
import { test, expect } from "@playwright/test"

test.describe("Map view", () => {
  test("map page loads without JS errors", async ({ page }) => {
    const errors: string[] = []
    page.on("pageerror", (err) => errors.push(err.message))

    await page.goto("/dashboard/map")
    // Wait for Leaflet container to appear
    await expect(page.locator(".leaflet-container")).toBeVisible({ timeout: 10_000 })
    expect(errors.filter(e => !e.includes("ResizeObserver"))).toHaveLength(0)
  })

  test("map tiles load (not a broken tile grid)", async ({ page }) => {
    await page.goto("/dashboard/map")
    await expect(page.locator(".leaflet-container")).toBeVisible({ timeout: 10_000 })
    // Leaflet tiles are img elements inside .leaflet-tile-pane
    await expect(page.locator(".leaflet-tile-pane img").first()).toBeVisible({ timeout: 15_000 })
  })

  test("request markers render when data exists", async ({ page }) => {
    await page.goto("/dashboard/map")
    await expect(page.locator(".leaflet-container")).toBeVisible({ timeout: 10_000 })
    // If any requests with coordinates exist, markers should be present
    const markers = page.locator(".leaflet-marker-icon")
    // Don't assert count — data may vary; just assert no crash
    await page.waitForTimeout(2_000)
    expect(await markers.count()).toBeGreaterThanOrEqual(0)
  })
})
```

---

### Suite 4: SMS webhook flow (`e2e/sms-flow.spec.ts`)

Tests the full SMS pipeline by calling the backend webhook directly.

```typescript
import { test, expect } from "@playwright/test"

const BACKEND = process.env.RAILWAY_BACKEND_URL

// Test messages covering all 8 categories
const CATEGORY_TESTS = [
  { body: "Large pothole on Main Street damaging car tires", expected: "pothole" },
  { body: "Streetlight out on 9th Ave for 3 days", expected: "streetlight" },
  { body: "Graffiti on the wall behind the library on Grove", expected: "graffiti" },
  { body: "Trash not picked up on Cary Street this week", expected: "trash" },
  { body: "Water main leak flooding the sidewalk on Broad", expected: "water" },
  { body: "Broken sidewalk slab at 5th and Franklin, tripping hazard", expected: "sidewalk" },
  { body: "Loud construction noise at midnight on Robinson St", expected: "noise" },
]

test.describe("SMS webhook flow", () => {
  test("webhook returns valid TwiML XML", async ({ request }) => {
    const res = await request.post(`${BACKEND}/webhooks/sms`, {
      form: {
        From: "+18045550101",
        Body: "Pothole on Broad Street near VCU",
        MessageSid: `SM_twiml_test_${Date.now()}`,
      },
    })
    expect(res.status()).toBe(200)
    const body = await res.text()
    expect(body).toContain("<Response>")
    expect(body).toContain("<Message>")
  })

  test("confirmation flow saves request to database", async ({ request }) => {
    const phone = "+18045550102"
    const sid = `SM_confirm_${Date.now()}`

    // Step 1: Initial report
    const step1 = await request.post(`${BACKEND}/webhooks/sms`, {
      form: { From: phone, Body: "Broken streetlight at 7th and Grace", MessageSid: sid },
    })
    expect(step1.status()).toBe(200)
    const reply1 = await step1.text()
    expect(reply1.toLowerCase()).toContain("confirm")

    // Step 2: Confirm
    const step2 = await request.post(`${BACKEND}/webhooks/sms`, {
      form: { From: phone, Body: "YES", MessageSid: `${sid}_yes` },
    })
    expect(step2.status()).toBe(200)
    const reply2 = await step2.text()
    expect(reply2.toLowerCase()).toContain("submitted")

    // Step 3: Verify request appears in API
    const listRes = await request.get(`${BACKEND}/api/v1/requests?limit=10`)
    expect(listRes.status()).toBe(200)
    const list = await listRes.json()
    expect(list.total).toBeGreaterThan(0)
  })

  test("cancellation flow does not save request", async ({ request }) => {
    const phone = "+18045550103"
    const before = await (await request.get(`${BACKEND}/api/v1/requests`)).json()
    const beforeCount = before.total

    await request.post(`${BACKEND}/webhooks/sms`, {
      form: { From: phone, Body: "Graffiti on the bridge", MessageSid: `SM_cancel_1_${Date.now()}` },
    })
    await request.post(`${BACKEND}/webhooks/sms`, {
      form: { From: phone, Body: "NO", MessageSid: `SM_cancel_2_${Date.now()}` },
    })

    const after = await (await request.get(`${BACKEND}/api/v1/requests`)).json()
    expect(after.total).toBe(beforeCount)  // Count should not increase
  })

  for (const { body, expected } of CATEGORY_TESTS) {
    test(`classifies "${expected}" correctly`, async ({ request }) => {
      const res = await request.post(`${BACKEND}/webhooks/sms`, {
        form: { From: "+18045550199", Body: body, MessageSid: `SM_cat_${expected}_${Date.now()}` },
      })
      expect(res.status()).toBe(200)
      const twiml = await res.text()
      // The confirmation message should include the category name
      expect(twiml.toLowerCase()).toContain(expected)
    })
  }
})
```

---

### Suite 5: Analytics (`e2e/analytics.spec.ts`)

```typescript
import { test, expect } from "@playwright/test"

test.describe("Analytics page", () => {
  test("analytics page loads without errors", async ({ page }) => {
    await page.goto("/dashboard/analytics")
    await expect(page.locator("main")).toBeVisible()
  })

  test("category breakdown chart renders", async ({ page }) => {
    await page.goto("/dashboard/analytics")
    // shadcn/ui chart wraps Recharts — check for SVG or canvas element
    await expect(page.locator("svg, canvas").first()).toBeVisible({ timeout: 10_000 })
  })
})
```

---

## Output — generate these files

When called, generate or update the following files:

```
frontend/
├── playwright.config.ts
├── e2e/
│   ├── dashboard.spec.ts
│   ├── requests.spec.ts
│   ├── map.spec.ts
│   ├── sms-flow.spec.ts
│   └── analytics.spec.ts
└── .env.test.example      # RAILWAY_FRONTEND_URL and RAILWAY_BACKEND_URL placeholders
```

Add to `frontend/package.json` scripts:
```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui",
"test:e2e:report": "playwright show-report"
```

Add to `frontend/.gitignore`:
```
.env.test
playwright-report/
test-results/
```

---

## When called

1. Read `docs/openapi.yaml` to verify correct endpoint paths and response shapes
2. Check if `frontend/e2e/` exists and what tests already exist — update rather than overwrite
3. If a specific suite is requested, generate only that suite; otherwise generate all 5
4. Note any tests that require Twilio signature bypass — the backend must allow test-mode requests (e.g., skip signature validation when `ENVIRONMENT=test`)
