# 7 - Incident / Outage Scenario Modeling

## Overview
Building pre-defined incident scenarios helps Dark NOC automatically recover from common failures with safe intent patterns.

## Goals
- Standardize incident runbook intents for major outage classes.
- Test network behavior and controls with scenario injection.
- Enable adaptive recovery based on actual impact.

## Components
1. Incident catalog
   - Template intents for congestions, link failure, DDoS, control-plane failure
2. Simulation framework
   - Inject faults in digital twin + validate recovery policies
3. Adaptive strategy selector
   - Pick actions based on historical success for each scenario
4. Post-incident learning
   - Add new scenario fingerprints and refine thresholds

## Workflow
1. Detect potential incident signature.
2. Match to incident template.
3. Execute safe recovery routine with checks.
4. Verify state and close the incident.

## Extra thoughts
- Include runbook variant for “soft failure” vs “hard failure”.
- Provide manual escalation if automated recovery fails twice.
- Auto-derive scenario IDs from telemetry patterns using supervised learning.

## Integration notes
- Incident models should leverage the same intent and policy schemas.
- Provide emergency mode endpoints to temporarily adjust aggressiveness.
- Capture with full audit logs for post-incident review.
