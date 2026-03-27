# Prompt: Distributed Source of Truth

Create a federated source-of-truth system design for distributed intent and state.

Inputs:
- multiple inventory sources (NetBox, CMDB, cloud APIs)
- topology/metadata updates

Outputs:
- canonical state representation
- drift detection reports
- reconciliation actions

Requirements:
- include data freshness scoring and versioning
- include conflict resolution strategy
- include API for read/query and write updates
