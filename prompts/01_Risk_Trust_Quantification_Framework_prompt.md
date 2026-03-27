# Prompt: Risk & Trust Quantification Framework

Design a risk and trust quantification module for autonomous networking.

Inputs:
- intent object
- policy evaluation result
- network state
- history of previous actions/outcomes

Outputs:
- risk_score (0-100)
- trust_score (0-100)
- safety decision (allow/warn/block)
- justification details (factors and provenance)

Requirements:
- deterministic, explainable, auditable
- includes safety budget logic and overload protection
- includes API contract and data model
- provide example JSON I/O

Extra:
- include a formula or algorithm for risk aggregation
- define threshold strategies for prod vs non-prod
