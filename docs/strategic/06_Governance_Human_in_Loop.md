# 6 - Governance Controls & Human-in-the-loop

## Overview
To be safe at scale, Dark NOC must balance automation with human governance and explicit decision escalation rules.

## Goals
- Define risk gating for automatic vs human approval.
- Record RBAC/ABAC context for every action.
- Provide strong audit trail with non-repudiation.

## Components
1. Governance engine
   - Accept risk scores, intent context, user attributes
   - Return mode: auto, manual review, block
2. Human approval workflow
   - Ticketing / action request with explanation
   - SLA on review times
3. Audit trail
   - Immutable logs with decision signatures
4. Policy hierarchy
   - Global guardrails + per-team allowances

## Workflow
1. Decision engine outputs candidate action + risk.
2. Governance engine checks policy + risk thresholds.
3. If manual required, create request and notify human operators.
4. Human approves/rejects; action proceeds or cancels.

## Extra thoughts
- Maintain a “war room mode” for incident response with different thresholds.
- Offer “trusted persona” bypass for pre-reviewed low-risk sections.
- Enable retrospective review (post-action analysis of auto vs manual decisions).

## Integration notes
- Should integrate with existing ITSM tools (ServiceNow, Jira).
- Provide API for policy dashboard and operator state.
- Use signed tokens for authorization decisions.
