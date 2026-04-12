# ANIF Platform — Living Architecture Document

> This document is maintained by the `architecture-agent`. Do not edit manually
> without also updating the relevant `.drawio` diagram files.

**Last updated by:** workspace scaffold
**Platform version:** 0.1.0 (scaffold only — no platform modules implemented yet)

---

## System Overview

The ANIF platform is a Python/FastAPI application that implements the Autonomous
Networking & Infrastructure Framework specification. It accepts network intents,
evaluates them against policies, scores their risk, makes bounded decisions,
executes approved actions, and records everything to an immutable audit trail.

---

## Backend Modules

| Module | Status | ANIF Spec |
|---|---|---|
| `schemas` | Not started | ANIF-300, ANIF-600 |
| `audit` | Not started | ANIF-107 |
| `policy` | Not started | ANIF-302, ANIF-303 |
| `risk` | Not started | ANIF-304 |
| `intent` | Not started | ANIF-300, ANIF-301 |
| `governance` | Not started | ANIF-301, ANIF-406 |
| `pipeline` | Not started | ANIF-305–308 |
| `agents` | Not started | ANIF-803, ANIF-805 |
| `auth` | Not started | ANIF-843 |
| `ethics` | Not started | ANIF-720–725 |
| `monitoring` | Not started | ANIF-401, ANIF-846 |
| `human_loop` | Not started | ANIF-402, ANIF-404 |
| `sot` | Scaffold only | ANIF-307 |

---

## Frontend Pages

| Page | Status | Backend Dependency |
|---|---|---|
| Intent Dashboard | Not started | B2 |
| Approval Queue | Not started | B4 |
| Audit Trail Viewer | Not started | B2 |
| Topology View | Not started | B5 |
| Risk & Governance | Not started | B8 |

---

## Diagrams

All diagrams are in `docs/architecture/diagrams/`. Open with draw.io or diagrams.net.

| File | Contents |
|---|---|
| `system-context.drawio` | Platform boundaries and external systems |
| `component.drawio` | Module breakdown and interfaces |
| `sequence-pipeline.drawio` | Intent → policy → risk → decision → governance → execution |
| `agent-tiers.drawio` | 4-tier agent model with capabilities |
| `data-flow.drawio` | Intent lifecycle and audit trail flow |
| `sot-integration.drawio` | SoT read/write-back boundaries |
| `deployment.drawio` | Docker services, ports, networking |

---

## External Systems

| System | Role | Connection |
|---|---|---|
| Nautobot / NetBox / InfraHub | Source of Truth | REST / GraphQL (read + metadata write-back) |
| PostgreSQL 15 | Audit trail, risk register | SQLAlchemy async |
| Redis 7 | Intent queue, message bus | redis-py async |
| Prometheus | Metrics collection | /metrics endpoint |
| Containerlab | Network simulation | CLI + topology YAML |
| Batfish | Static config analysis | pybatfish |
