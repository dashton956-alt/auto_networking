# 4 - Policy Conflict Resolution & Precedence

## Overview
Policy conflict resolution is critical to avoid inconsistent actions and improve trust. Policies across compliance, availability, and reliability must be explicitly ordered and explainable.

## Goals
- Detect conflicting policies before execution.
- Provide precedence semantics (explicit and default).
- Give detailed conflict explanation and remediation.

## Components
1. Policy parser
   - Normalize rules into controlled logic tree.
2. Conflict detector
   - Identify contradictions and overlapping scopes.
3. Precedence engine
   - Apply user-defined tiers (e.g., compliance>availability>performance)
   - Implement policy grouping and negotiation.
4. Conflict report
   - Provide actionable items: "deny this rule" or "scope adjustment".

## Workflow
1. Ingest policy set for a given service.
2. Compute policy relationships and potential conflicts.
3. If conflict, choose resolution path or escalate for manual review.
4. Enforce resolved policy set in `policy_engine`.

## Extra thoughts
- Include an “approximate solve” mode for best-effort action when full resolution not possible.
- Support policy templates and policy inheritance to reduce owner errors.
- Add trace ID mapping for each policy decision path.

## Integration notes
- Tie with `policy_schema.yml` and add metadata for precedence level.
- Add UI/CLI to drill into conflicts and approval history.
- Ensure deterministic output for same inputs every run.
