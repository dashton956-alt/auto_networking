# 5 - Distributed Source-of-Truth

## Overview
A federated source-of-truth is essential for scaling beyond single-zone operation. It includes fallbacks, versions, and reconciliation for consistency.

## Goals
- Model canonical intent and topology across multi-vendor, multi-region sources.
- Prevent drift and stale decisions from out-of-date data.
- Provide agreed-upon state for all control decisions.

## Components
1. Source interfaces
   - Connectors to NetBox, CMDB, cloud inventories (AWS/GCP/Azure), and custom APIs.
2. Federation layer
   - Merge and prioritize conflicting source values.
3. Versioned graph store
   - Time-travel capabilities and change history.
4. Drift detector
   - Alert when prod config diverges from intended state.

## Workflow
1. Periodic sync from each data source.
2. Build canonical view and validate with schema.
3. Publish state to policy/decision engines.
4. On anomalies, trigger reconciliation actions.

## Extra thoughts
- Add a “latency” score to each source to prioritize fresh data.
- Include raw timestamp and health status in the metadata for each field.
- Support isolated read replicas for analytical queries so engines stay performant.

## Integration notes
- This is the gate for all detection and enforcement.
- Keep API strongly typed and include fallback plan for partial outages.
- Ensure security and role-based access for truth sources.
