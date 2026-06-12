# F6: Risk & Governance Dashboard — Implementation Plan

Date: 2026-06-12
Specs: ANIF-401/846 (observability), ANIF-721 §7 (strikes), ANIF-902–907 (councils)
Backend dependency: B8 — complete
WCAG 2.1 AA required (enforced by Playwright/axe)

## Scope (design spec §16)

Live risk score panels, council decision feed, ethics strikes log,
observability metrics.

## Backend slice (TDD)

1. **`GET /council/sessions?limit=`** — recent council records newest-first:
   council_id, council_type, decision, triggered_by, trigger_timestamp,
   session_close_timestamp, decision_rationale, intent_id. Auth required.
2. **`GET /ethics/strikes?limit=`** — recent strike_records newest-first:
   strike_id, agent_id, intent_id, reason, recorded_at. Auth required.
   (Reads the durable append-only table; note: the production DB-backed
   strike writer is still a B7 gap — the live log is empty until it lands.)
3. **Mount `/metrics`** — prometheus_client ASGI app. The compose Prometheus
   already scrapes `platform:8000/metrics`; today that 404s. Unauthenticated
   by convention (scraper has no key) — counters carry no sensitive payload.

## Frontend

```
src/anif_ui/src/
  api/dashboard.ts        ← getCouncilSessions, getStrikes types + calls
  pages/GovernancePage.tsx ← /governance (replaces placeholder)
```

### GovernancePage panels (auto-refresh every 15s + manual Refresh)

1. **Live risk panel** — `GET /audit?stage=risk&limit=10`: most recent
   intent's RiskMeter (risk + trust) plus a recent-scores list with
   safety-decision badges and intent links.
2. **Governance activity (observability)** — `GET /audit?stage=governance&limit=50`
   aggregated client-side: auto / manual_review / block counts with
   percentage bars, total evaluated, link note to /metrics for Prometheus.
3. **Council decision feed** — `GET /council/sessions`: type + decision
   badges, triggered_by, rationale, intent link, close timestamp.
4. **Ethics strikes log** — `GET /ethics/strikes`: agent, intent link,
   reason, recorded_at; explanatory empty state (append-only record).

## WCAG / tests
- axe audit: /governance with all four panels mocked — 0 violations
- Live UAT: seed risk/governance records via /orchestrate +
  /governance/check, open council sessions via POST /council/*, insert a
  sample strike row via SQL; verify all panels render live data;
  curl /metrics returns Prometheus text

## Task order
1. Backend TDD: failing tests (council sessions, strikes, metrics mount) → implement → green
2. api/dashboard.ts + GovernancePage + route swap
3. axe audit — 0 violations
4. Gates + live UAT + architecture doc + commits
