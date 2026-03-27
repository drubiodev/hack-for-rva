---
description: Generate Playwright e2e tests targeting the deployed Railway URL — covers document upload, processing pipeline, dashboard UI, and analytics
---

Generate Playwright e2e tests for the HackathonRVA Procurement Document Processing service. All tests run against the **deployed Railway URLs** — no localhost, no mocks.

---

## Test philosophy for this PoC

- **No unit tests, no mocking** — test the real deployed system end-to-end
- **Minimal but meaningful** — cover the demo critical path; skip edge cases that don't affect the demo
- **Seed via API** — tests that need data upload sample PDFs via `POST /api/v1/documents/upload`
- **Fast** — entire suite should complete in under 2 minutes
- **Idempotent** — tests should not break if run multiple times against a database that already has data

---

## Playwright configuration

```typescript
// playwright.config.ts (place at procurement/frontend/ root)
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

---

## Test suites

### Suite 1: Dashboard overview (`e2e/dashboard.spec.ts`)

```typescript
import { test, expect } from "@playwright/test"

test.describe("Dashboard overview", () => {
  test("dashboard page loads without errors", async ({ page }) => {
    await page.goto("/dashboard")
    await expect(page.locator("main")).toBeVisible()
  })

  test("KPI cards are visible", async ({ page }) => {
    await page.goto("/dashboard")
    await expect(page.locator("[data-testid='kpi-card']").first()).toBeVisible()
  })

  test("navigation links work", async ({ page }) => {
    await page.goto("/dashboard")
    await page.getByRole("link", { name: /upload/i }).click()
    await expect(page).toHaveURL(/\/dashboard\/upload/)
    await page.getByRole("link", { name: /documents/i }).click()
    await expect(page).toHaveURL(/\/dashboard\/documents/)
    await page.getByRole("link", { name: /analytics/i }).click()
    await expect(page).toHaveURL(/\/dashboard\/analytics/)
  })
})
```

---

### Suite 2: Document upload and processing (`e2e/upload.spec.ts`)

```typescript
import { test, expect } from "@playwright/test"
import path from "path"

const BACKEND = process.env.RAILWAY_BACKEND_URL

test.describe("Document upload", () => {
  test("upload page renders with drop zone", async ({ page }) => {
    await page.goto("/dashboard/upload")
    await expect(page.locator("main")).toBeVisible()
    // Drop zone should be visible
    await expect(page.getByText(/drop|upload/i).first()).toBeVisible()
  })

  test("uploading a PDF via API returns 202", async ({ request }) => {
    const res = await request.post(`${BACKEND}/api/v1/documents/upload`, {
      multipart: {
        file: {
          name: "test-contract.pdf",
          mimeType: "application/pdf",
          buffer: Buffer.from("test pdf content"),
        },
      },
    })
    expect(res.status()).toBe(202)
    const body = await res.json()
    expect(body.id).toBeDefined()
    expect(body.status).toBe("uploading")
  })
})
```

---

### Suite 3: Document list (`e2e/documents.spec.ts`)

```typescript
import { test, expect } from "@playwright/test"

test.describe("Document list", () => {
  test("document table renders", async ({ page }) => {
    await page.goto("/dashboard/documents")
    await expect(page.getByRole("table")).toBeVisible()
  })

  test("status filter narrows results", async ({ page }) => {
    await page.goto("/dashboard/documents")
    // Table should render even with filter applied
    await expect(page.getByRole("table")).toBeVisible()
  })

  test("clicking a document opens the detail view", async ({ page }) => {
    await page.goto("/dashboard/documents")
    const firstRow = page.getByRole("row").nth(1)
    if (await firstRow.isVisible()) {
      await firstRow.click()
      await expect(page).toHaveURL(/\/dashboard\/documents\//)
    }
  })
})
```

---

### Suite 4: Document detail (`e2e/document-detail.spec.ts`)

```typescript
import { test, expect } from "@playwright/test"

const BACKEND = process.env.RAILWAY_BACKEND_URL

test.describe("Document detail", () => {
  test("detail page shows extracted fields and validation results", async ({ request, page }) => {
    // Get first document from API
    const listRes = await request.get(`${BACKEND}/api/v1/documents?limit=1`)
    const list = await listRes.json()
    if (list.items.length === 0) {
      test.skip()
      return
    }
    const docId = list.items[0].id

    await page.goto(`/dashboard/documents/${docId}`)
    await expect(page.locator("main")).toBeVisible()
    // Processing stepper or extracted fields should be visible
    await expect(page.locator("main").getByText(/status|type|vendor|amount/i).first()).toBeVisible({ timeout: 10_000 })
  })
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

  test("risk summary section renders", async ({ page }) => {
    await page.goto("/dashboard")
    // Look for risk-related content (expiring contracts, deadlines)
    await expect(page.locator("main")).toBeVisible()
  })
})
```

---

## Output — generate these files

```
procurement/frontend/
├── playwright.config.ts
├── e2e/
│   ├── dashboard.spec.ts
│   ├── upload.spec.ts
│   ├── documents.spec.ts
│   ├── document-detail.spec.ts
│   └── analytics.spec.ts
└── .env.test.example
```

---

## When called

1. Read `procurement/docs/openapi.yaml` to verify correct endpoint paths and response shapes
2. Check if `procurement/frontend/e2e/` exists and what tests already exist — update rather than overwrite
3. If a specific suite is requested, generate only that suite; otherwise generate all 5
4. Use sample PDF files from `procurement/backend/scripts/` for upload tests if available
