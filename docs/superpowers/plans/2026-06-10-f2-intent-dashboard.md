# F2: Intent Dashboard — Implementation Plan

Date: 2026-06-10
Specs: ANIF-300 (intent model), ANIF-301 (validation/registry API), ANIF-107 §4.5 (audit query)
Backend dependency: B2 Intent API — complete
WCAG 2.1 AA required on every page (enforced by Playwright/axe)

## Scope (from workspace design spec §16)

F2 delivers four things:
1. **Intent submission form** — structured form mapping 1:1 to the Intent schema
2. **Intent list view** — registered intents, newest first
3. **Pipeline status tracker** — six-stage progress visual
4. **Intent detail view** — resolved intent, provenance, audit timeline, "why"

## Backend gap: intent list endpoint

The B2 Intent API has `register`/`get` but no list. The dashboard list view
requires one. Addition (TDD — tests first):

- `IntentRegistry.list(limit, offset, status?, service?) -> tuple[list[ValidatedIntent], int]`
  ordered `created_at DESC`, capped `limit <= 100`
- `GET /intent/intents?limit&offset&status&service` → `IntentListResponse
  {items, total, limit, offset}` (auth: X-API-Key like all endpoints)
- Unit tests: ordering, pagination, filters, empty list, cap

No other backend change. The UI consumes existing endpoints for everything else:
`POST /intent/validate-intent`, `POST /orchestrate`, `GET /intent/intent/{id}`,
`GET /audit/{id}`, `GET /audit/{id}/why`.

## Frontend architecture

```
src/anif_ui/src/
  api/
    client.ts        ← fetch wrapper: base /api, X-API-Key header, error type
    types.ts         ← ValidatedIntent, ValidationResult, OrchestrateResponse,
                       AuditRecord, IntentListResponse, PipelineStage types
    intents.ts       ← listIntents, getIntent, validateIntent, orchestrate,
                       getAuditRecords, getAuditWhy
  components/
    PipelineStatusTracker.tsx  ← 6 stages; pass/fail/blocked/pending_approval/
                                 dry_run/skipped states; ARIA ol
  pages/
    IntentListPage.tsx    ← / (replaces placeholder)
    IntentSubmitPage.tsx  ← /intents/new
    IntentDetailPage.tsx  ← /intents/:intentId
```

- **Dev proxy:** vite proxies `/api/*` → `http://localhost:8000` (path rewrite
  strips `/api`). Avoids CORS; mirrors production gateway layout.
- **API key:** `VITE_ANIF_API_KEY` env var (dev only — auth is a B-track
  placeholder until X.509 wiring). Add to `.env.example`.
- **No new deps** — fetch + React state; data needs don't justify a query lib yet.

## Page behaviour

### IntentListPage (/)
- Table: change #, service, environment, status Badge, warnings count, created
- Pagination (limit 20), refresh button, loading Skeleton, error Alert, empty state
- Row click → `/intents/:id`; "New Intent" Button → `/intents/new`

### IntentSubmitPage (/intents/new)
- Form fields mirroring Intent schema exactly (no gold-plating):
  service (Input, required), environment (Select), priority (Select),
  objectives.latency_ms / availability_percent / throughput_mbps (numeric Inputs),
  constraints.region (Select), constraints.encryption (checkbox),
  constraints.allowed_zones (comma-separated Input), policies (checkbox group)
- Buttons: **Validate** (validate-intent only), **Dry run** (orchestrate
  dry_run=true), **Submit** (orchestrate)
- Result panel: validation errors/warnings as Alerts; orchestrate result rendered
  as PipelineStatusTracker + outcome Alert (incl. pending_approval ticket id)
- On `pipeline_complete`/registered: link to detail page

### IntentDetailPage (/intents/:intentId)
- Summary Card: service, change #, status, environment, created, git provenance
- Pipeline status tracker derived from `GET /audit/{id}` records
  (stage → outcome mapping; stages with no record = pending/not reached)
- "Why" panel: `GET /audit/{id}/why` text
- Warnings Alerts; resolved intent as collapsible `<details>` JSON
- 404 handling: Alert + back link

### PipelineStatusTracker
- Props: ordered stage results (validate, policy, risk, decision, governance, execute)
- Visual: numbered steps with status colour + icon; `<ol>` with aria-current and
  sr-only status text; colours from F1 status/intent tokens

## WCAG / tests

- Extend `tests/accessibility` axe audit to `/`, `/intents/new`, `/intents/:id`
  with **Playwright route mocking** (`page.route('**/api/**')`) so audits are
  hermetic — no live backend in CI
- Audit must pass with 0 violations (wcag2a + wcag2aa tags)
- Form labels: every Input/Select already enforces label association (F1)

## Task order

1. Backend TDD: failing tests for `IntentRegistry.list` + `GET /intent/intents` → implement → green
2. `api/types.ts` + `api/client.ts` + `api/intents.ts`
3. `PipelineStatusTracker` component
4. `IntentListPage` + routing swap
5. `IntentSubmitPage`
6. `IntentDetailPage`
7. vite proxy + `.env.example` + App.tsx routes/titles
8. Playwright axe audits (3 pages, mocked API) — 0 violations
9. Quality gates: ruff/black/mypy strict (backend), eslint/tsc/build (frontend), full pytest
10. Architecture doc update + commit
