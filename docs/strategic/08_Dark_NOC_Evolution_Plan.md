# 8 - Dark NOC Evolution Plan

## Overview
A maturity model with explicit gating is needed to safely move from manual to Dark NOC.

## Goals
- Define progression criteria for each level (0
4).
- Standardize KPI and compliance checks per stage.
- Ensure rollback paths are planned and tested.

## Components
1. Level definitions
   - Level 0: manual operations
   - Level 1: scripted automation
   - Level 2: AI-assisted ops
   - Level 3: conditional autonomy
   - Level 4: Dark NOC partial autonomy
2. Entry/exit criteria
   - Risk metrics, coverage, incident rates
3. Stage gates
   - Validation people, capability, tooling
4. Reporting
   - Dashboard for maturity status and next milestones

## Workflow
1. Assess current state against criteria.
2. Implement required tooling and delta controls.
3. Certify readiness and promote stage.
4. Periodic re-assessment and regulation.

## Extra thoughts
- Include “no-go conditions” that force step-back (e.g., rising MTTR).
- Use metrics tied to ability to implement each strategy point from doc.
- Align stages with business impact policies (e.g., 80% automation target at Level 4).

## Integration notes
- Output should feed into Roadmap and governance panels.
- Should be executable as an audit checklist for stakeholders.
