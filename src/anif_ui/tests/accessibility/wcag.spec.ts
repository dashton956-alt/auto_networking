import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const INTENT_ID = "7f9b2a64-1c3d-4e5f-8a9b-0c1d2e3f4a5b";

const VALIDATED_INTENT = {
  intent_id: INTENT_ID,
  change_number: 42,
  version: "0.1.0",
  service: "payments",
  status: "validated",
  git_ref: {
    repo_url: "https://git.example.com/intents.git",
    path: "intents/payments.yml",
    commit_sha: "abc123def4567890abc123def4567890abc123de",
  },
  resolved_intent: {
    service: "payments",
    environment: "staging",
    priority: "high",
    objectives: { latency_ms: 50 },
    constraints: { region: "EU", encryption: true },
    policies: ["zero_trust"],
  },
  warnings: ["objectives.latency_ms: value below 10 ms is unlikely to be achievable"],
  created_at: "2026-06-10T09:00:00Z",
};

const AUDIT_RECORDS = [
  {
    record_id: "0a1b2c3d-0000-4000-8000-000000000001",
    intent_id: INTENT_ID,
    stage: "validate",
    timestamp: "2026-06-10T09:00:01Z",
    outcome: "success",
    duration_ms: 12,
    input_summary: { service: "payments" },
    output_summary: { status: "validated" },
  },
  {
    record_id: "0a1b2c3d-0000-4000-8000-000000000002",
    intent_id: INTENT_ID,
    stage: "policy",
    timestamp: "2026-06-10T09:00:02Z",
    outcome: "success",
    duration_ms: 8,
    input_summary: {},
    output_summary: { overall_result: "pass" },
  },
  {
    record_id: "0a1b2c3d-0000-4000-8000-000000000003",
    intent_id: INTENT_ID,
    stage: "risk",
    timestamp: "2026-06-10T09:00:03Z",
    outcome: "success",
    duration_ms: 5,
    input_summary: {},
    output_summary: { risk_score: 35 },
  },
  {
    record_id: "0a1b2c3d-0000-4000-8000-000000000004",
    intent_id: INTENT_ID,
    stage: "governance",
    timestamp: "2026-06-10T09:00:04Z",
    outcome: "escalated",
    duration_ms: 3,
    input_summary: {},
    output_summary: { mode: "manual_review" },
  },
];

const TICKET = {
  ticket_id: "GOV-20260611-001",
  intent_id: INTENT_ID,
  requested_by: "pipeline-automation",
  risk_score: 74,
  decision_summary: "apply_qos on staging requires senior_engineer approval",
  created_at: "2026-06-11T09:00:00Z",
  expires_at: new Date(Date.now() + 14 * 60 * 1000).toISOString(),
};

/** Mock every /api route the F2/F3 pages call so audits run without a backend. */
async function mockApi(page: Page) {
  await page.route("**/api/intent/intents**", (route) =>
    route.fulfill({
      json: { items: [VALIDATED_INTENT], total: 1, limit: 20, offset: 0 },
    }),
  );
  await page.route(`**/api/intent/intent/${INTENT_ID}`, (route) =>
    route.fulfill({ json: VALIDATED_INTENT }),
  );
  await page.route(`**/api/audit/${INTENT_ID}`, (route) =>
    route.fulfill({ json: AUDIT_RECORDS }),
  );
  await page.route(`**/api/audit/${INTENT_ID}/why`, (route) =>
    route.fulfill({
      json: `Intent ${INTENT_ID} — pipeline summary\n\nStage: validate → success\nStage: governance → escalated`,
    }),
  );
  await page.route("**/api/governance/tickets", (route) =>
    route.fulfill({ json: { pending_count: 1, tickets: [TICKET] } }),
  );
  await page.route(`**/api/audit/${INTENT_ID}/verify`, (route) =>
    route.fulfill({ json: { valid: true, broken_at: null, record_count: 4 } }),
  );
  // Regexes anchored at end-of-path/query: bare globs like "**/api/topology**"
  // also match vite module URLs (/src/api/topology.ts) and break the app.
  await page.route(/\/api\/audit(\?|$)/, (route) => {
    const url = new URL(route.request().url());
    if (url.searchParams.get("stage") === "risk") {
      return route.fulfill({
        json: [
          {
            record_id: "0a1b2c3d-0000-4000-8000-000000000003",
            intent_id: INTENT_ID,
            stage: "risk",
            timestamp: "2026-06-12T09:00:03Z",
            outcome: "success",
            duration_ms: 5,
            input_summary: {},
            output_summary: { risk_score: 62, trust_score: 78, safety_decision: "warn" },
          },
          {
            record_id: "0a1b2c3d-0000-4000-8000-000000000013",
            intent_id: INTENT_ID,
            stage: "risk",
            timestamp: "2026-06-12T08:00:03Z",
            outcome: "success",
            duration_ms: 4,
            input_summary: {},
            output_summary: { risk_score: 21, trust_score: 90, safety_decision: "allow" },
          },
        ],
      });
    }
    if (url.searchParams.get("stage") === "governance") {
      return route.fulfill({
        json: [
          {
            record_id: "0a1b2c3d-0000-4000-8000-000000000004",
            intent_id: INTENT_ID,
            stage: "governance",
            timestamp: "2026-06-12T09:00:04Z",
            outcome: "escalated",
            duration_ms: 3,
            input_summary: {},
            output_summary: { mode: "manual_review" },
          },
          {
            record_id: "0a1b2c3d-0000-4000-8000-000000000014",
            intent_id: INTENT_ID,
            stage: "governance",
            timestamp: "2026-06-12T08:00:04Z",
            outcome: "success",
            duration_ms: 2,
            input_summary: {},
            output_summary: { mode: "auto" },
          },
        ],
      });
    }
    return route.fulfill({ json: AUDIT_RECORDS });
  });
  await page.route(/\/api\/council\/sessions(\?|$)/, (route) =>
    route.fulfill({
      json: {
        total: 2,
        sessions: [
          {
            council_id: "c-1",
            council_type: "runtime",
            decision: "approved",
            triggered_by: "intent execution timeout exceeded",
            trigger_timestamp: "2026-06-12T09:05:00Z",
            session_close_timestamp: "2026-06-12T09:08:00Z",
            decision_rationale: "Risk within tolerance; execution may continue",
            intent_id: INTENT_ID,
          },
          {
            council_id: "c-2",
            council_type: "review",
            decision: "completed",
            triggered_by: "post-incident review of blocked intent",
            trigger_timestamp: "2026-06-12T08:00:00Z",
            session_close_timestamp: null,
            decision_rationale: null,
            intent_id: null,
          },
        ],
      },
    }),
  );
  await page.route(/\/api\/ethics\/strikes(\?|$)/, (route) =>
    route.fulfill({
      json: {
        total: 1,
        strikes: [
          {
            strike_id: "s-1",
            agent_id: "9e107d9d-372b-4b66-8a0e-95f0a1b2c3d4",
            intent_id: INTENT_ID,
            reason: "acted outside declared capabilities",
            recorded_at: "2026-06-12T07:45:00Z",
          },
        ],
      },
    }),
  );
  await page.route(/\/api\/topology(\?|$)/, (route) =>
    route.fulfill({
      json: {
        site: "lab-1",
        devices: [
          {
            name: "spine-1",
            role: "spine",
            platform: "frr",
            primary_ip: "10.0.0.1",
            tags: ["intent:abc"],
            custom_fields: {
              intent_status: "success",
              last_intent_id: INTENT_ID,
              intent_applied_at: "2026-06-11T09:00:00Z",
            },
            interfaces: [
              { name: "eth1", ip_address: "10.1.1.0/31", tags: [] },
              { name: "eth2", ip_address: "10.1.2.0/31", tags: ["intent:abc"] },
            ],
          },
          {
            name: "leaf-1",
            role: "leaf",
            platform: "frr",
            primary_ip: "10.0.0.11",
            tags: [],
            custom_fields: { intent_status: "failed" },
            interfaces: [{ name: "eth1", ip_address: "10.1.1.1/31", tags: [] }],
          },
          {
            name: "host-1",
            role: "host",
            platform: "linux",
            primary_ip: null,
            tags: [],
            custom_fields: {},
            interfaces: [],
          },
        ],
        connections: [
          ["spine-1", "leaf-1"],
          ["leaf-1", "host-1"],
        ],
      },
    }),
  );
}

async function expectNoViolations(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();
  expect(results.violations).toEqual([]);
}

test.describe("WCAG 2.1 AA audit", () => {
  test("intent list page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto("/");
    await page.getByRole("link", { name: "payments" }).waitFor();
    await expectNoViolations(page);
  });

  test("intent submission page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto("/intents/new");
    await page.getByRole("button", { name: "Submit intent" }).waitFor();
    await expectNoViolations(page);
  });

  test("intent detail page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto(`/intents/${INTENT_ID}`);
    await page.getByRole("heading", { name: "payments" }).waitFor();
    await expectNoViolations(page);
  });

  test("approval queue page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto("/approvals");
    await page.getByRole("link", { name: TICKET.ticket_id }).waitFor();
    await expectNoViolations(page);
  });

  test("ticket review page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto(`/approvals/${TICKET.ticket_id}`);
    await page.getByRole("button", { name: "Approve…" }).waitFor();
    await expectNoViolations(page);
  });

  test("ticket review confirmation step has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto(`/approvals/${TICKET.ticket_id}`);
    await page.getByRole("button", { name: "Reject…" }).click();
    await page.getByRole("button", { name: "Confirm rejection" }).waitFor();
    await expectNoViolations(page);
  });

  test("audit trail page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto("/audit");
    await page.getByRole("button", { name: "Apply filters" }).waitFor();
    // Expand a reasoning row so the expanded state is audited too.
    await page.getByRole("button", { name: /Expand reasoning for governance/ }).click();
    await page.getByText("Reasoning chain").first().waitFor();
    await expectNoViolations(page);
  });

  test("intent timeline page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto(`/audit/${INTENT_ID}`);
    await page.getByText("Hash chain verified").waitFor();
    await page.getByRole("button", { name: "Show reasoning" }).first().click();
    await expectNoViolations(page);
  });

  test("topology page has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto("/topology");
    await page.getByRole("img", { name: /Network topology for site lab-1/ }).waitFor();
    // Select a different device via the accessible list, then audit.
    await page.getByRole("button", { name: /leaf-1/ }).click();
    await page.getByRole("heading", { name: "leaf-1" }).waitFor();
    await expectNoViolations(page);
  });

  test("governance dashboard has no accessibility violations", async ({ page }) => {
    await mockApi(page);
    await page.goto("/governance");
    await page.getByText("Live risk scores").waitFor();
    await page.getByText("acted outside declared capabilities").waitFor();
    await expectNoViolations(page);
  });

  test("design system page has no accessibility violations", async ({ page }) => {
    await page.goto("/design-system");
    await expectNoViolations(page);
  });
});
