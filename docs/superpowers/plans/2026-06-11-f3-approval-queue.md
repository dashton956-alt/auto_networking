# F3: Approval Queue UI — Implementation Plan

Date: 2026-06-11
Specs: ANIF-404 §4.4–4.7 (human review interface), ANIF-406 (governance gate)
Backend dependency: B4 Approval Queue API — complete
WCAG 2.1 AA required on every page (enforced by Playwright/axe)

## Scope (design spec §16)

Human-in-loop review interface, approve/reject controls, approval ticket
timer display. Consumes existing endpoints only — **no backend changes**:

- `GET /governance/tickets` → `{pending_count, tickets: [...]}` (pending only)
- `POST /governance/approve/{ticket_id}` — headers `X-Operator-Id`,
  `X-Operator-Roles`; body `{approver_role, notes?}`
- `POST /governance/reject/{ticket_id}` — same headers; body `{reason}`
- `GET /intent/intent/{id}`, `GET /audit/{id}`, `GET /audit/{id}/why` (already typed)

Server-side rules the UI must surface: approve needs `senior_engineer` (403),
reject needs `network_engineer`+ (403), self-approval 403, non-pending 409,
expired 410-ish via TicketError. RBAC is enforced server-side; the UI's
operator identity is advisory until X.509 auth lands.

## ANIF-404 §4.7 MUST elements → ticket review page

| Element | Source |
|---|---|
| Intent summary | ticket `decision_summary` |
| Proposed action details | `resolved_intent` JSON from intent endpoint |
| Risk score | ticket `risk_score` (RiskMeter) |
| Risk score justification | risk-stage audit record output_summary + reasoning |
| Full reasoning chain | `GET /audit/{id}/why` |
| Governance rule triggered | governance-stage record (triggered_rule + rationale) |
| Rollback plan | derived from decision-stage recommended_action (pipeline contract: reverse action within 60s, target pipeline-auto); "Not yet generated" if absent |
| Countdown timer | `expires_at` → existing CountdownTimer |
| Submitter identity | ticket `requested_by` |
| Policy evaluation results | policy-stage record policies_evaluated/violated |

Also MUST: clearly labelled Approve/Reject **with a confirmation step**.

## Frontend architecture

```
src/anif_ui/src/
  api/governance.ts      ← listTickets, approveTicket, rejectTicket + types
  api/client.ts          ← extend RequestOptions with headers
  components/OperatorBar.tsx ← "Acting as" identity control (id + role select)
  pages/ApprovalQueuePage.tsx  ← /approvals (replaces placeholder)
  pages/TicketReviewPage.tsx   ← /approvals/:ticketId
```

### ApprovalQueuePage (/approvals)
- Pending tickets table: ticket id, intent link, summary, risk badge,
  requested_by, created, **live countdown** (CountdownTimer), Review link
- Queue-depth warning Alert when >5 pending (ANIF-404 §7 operational signal)
- Refresh button, loading skeleton, error/empty states

### TicketReviewPage (/approvals/:ticketId)
- Ticket located via the pending list; if absent → "no longer pending" Alert
- All §4.7 elements above; pipeline progress strip reused from F2
- OperatorBar (operator id input + role select: network_engineer /
  senior_engineer) — sent as X-Operator-Id / X-Operator-Roles
- Approve → confirmation panel (optional notes + Confirm approval)
- Reject → confirmation panel (required reason + Confirm rejection)
- Outcome Alert (approved/rejected/error incl. 403 self-approval, 409
  not-pending), then link back to queue

## WCAG / tests

- Extend axe audits: `/approvals` and `/approvals/:ticketId` with mocked
  API (route interception), 0 violations required
- Countdown timers use existing aria-live CountdownTimer

## Task order

1. `api/governance.ts` types + calls; client header support
2. OperatorBar component
3. ApprovalQueuePage + route swap
4. TicketReviewPage (review elements, confirm flows)
5. axe audits (2 pages, mocked API) — 0 violations
6. Gates: eslint, tsc build, backend suite untouched-but-run
7. Architecture doc update + commit
