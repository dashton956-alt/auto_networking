# 9 - Observability & Explainability Artifacts

## Overview
Transparent decision logs and explainable output are vital for operator trust and compliance.

## Goals
- Capture causal chain for every decision.
- Provide APIs for "why" questions.
- Generate SLA/SLO scorecards from intent evaluations.

## Components
1. Decision audit log
   - intent_id, policy_results, risk_score, action, outcome
2. Explainability service
   - `/why-decision` and `/why-denied` APIs
   - human-readable rationale
3. Metrics dashboards
   - policy compliance %, automatic approval %, risk distribution
4. Alerting
   - anomalies in decision logic (e.g., sudden high-deny rate)

## Workflow
1. Each engine emits telemetry event with full context.
2. Observability layer ingests and indexes.
3. Engineers query explainability API or dashboard.
4. Feedback can iterate policy engine.

## Extra thoughts
- Represent the decision graph as JSON for higher-level visualization.
- Include confidence breakdown and graded trust per source.
- Archive explainability data for regulated retention windows.

## Integration notes
- This can be implemented as an event stream consumer (Kafka/ELK).
- Keep retained raw data immutable for audit.
