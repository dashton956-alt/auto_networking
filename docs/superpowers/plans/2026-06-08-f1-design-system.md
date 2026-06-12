# F1: Design System — Implementation Plan

Date: 2026-06-08
Specs: ANIF-404 §4.7 (human review interface requirements)
WCAG 2.1 AA required on every component (enforced by Playwright/axe)

## MUSTs from ANIF-404 §4.7 that shape the design system

The approval queue UI MUST display:
- Intent summary, risk score, risk score justification, full reasoning chain
- Governance rule triggered, rollback plan
- Time remaining before expiry (CountdownTimer)
- Submitter identity
- Policy evaluation results

These drive the component shapes for F3 — F1 lays the tokens and primitives.

## Design Tokens (Tailwind config)

- Full brand palette (50-950, blue-based)
- Semantic status colors: success, warning, danger, info
- Risk threshold colors: risk-low (0-30), risk-medium (31-69), risk-high (70-100)
- Intent/ticket status badges: pending, running, success, failed, blocked, escalated

## Components to Build

1. Button — primary/secondary/danger/ghost + sm/md/lg + loading + disabled
2. Badge — colored label, status variants
3. Card — content panel with header/body/footer slots
4. Table — sortable headers, loading state, empty state
5. Input — text input with label, helper text, error state
6. Select — dropdown with label and error state
7. Alert — success/warning/error/info banners with dismiss
8. Spinner — loading indicator (sm/md/lg)
9. Skeleton — content placeholder bars
10. RiskMeter — 0-100 bar with threshold coloring + numeric label
11. CountdownTimer — live countdown (ANIF-404 §4.7 — time remaining before expiry)
12. AppShell + Sidebar + TopBar — layout primitives

## File Structure

```
src/anif_ui/src/
  components/
    Button.tsx, Badge.tsx, Card.tsx, Table.tsx
    Input.tsx, Select.tsx, Alert.tsx
    Spinner.tsx, Skeleton.tsx
    RiskMeter.tsx, CountdownTimer.tsx
    index.ts
  layouts/
    Sidebar.tsx, TopBar.tsx, AppShell.tsx
  pages/
    DesignSystemPage.tsx    ← live showcase at /design-system
```

## Tasks

1. Expand tailwind.config.js with full design tokens
2. Update vite.config.ts with @ path alias
3. Build primitive components (Button, Badge, Card, Alert, Spinner, Skeleton)
4. Build form components (Input, Select)
5. Build Table component
6. Build data components (RiskMeter, CountdownTimer)
7. Build AppShell layout (Sidebar, TopBar)
8. Build DesignSystemPage showcase
9. Update App.tsx routing + WCAG audit pass
