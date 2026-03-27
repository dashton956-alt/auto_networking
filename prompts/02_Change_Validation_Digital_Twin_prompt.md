# Prompt: Change Validation / Digital Twin Simulation

Define a change validation and digital twin simulation architecture for intent-driven network actions.

Inputs:
- intent/drift proposed change
- canonical current network model
- policy rule set

Outputs:
- simulation verdict (pass/fail)
- impact metrics (latency, failed paths, reachability)
- recommended mitigations and rollback plan

Requirements:
- include topology modelling and state refresh from source-of-truth
- support multiple what-if scenarios
- include APIs and sequence flow
- include conflict/resolution path when policy fails
