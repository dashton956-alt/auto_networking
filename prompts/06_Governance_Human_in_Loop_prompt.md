# Prompt: Governance Controls & Human-in-loop

Define governance and human-in-loop controls for a Dark NOC orchestration system.

Inputs:
- candidate action + risk score
- user identity and roles
- policy guardrails

Outputs:
- mode (auto/manual/block)
- review ticketing payload
- audit record schema

Requirements:
- include RBAC/ABAC policy checks
- include war-room mode and emergency path
- include integration with ITSM service request
