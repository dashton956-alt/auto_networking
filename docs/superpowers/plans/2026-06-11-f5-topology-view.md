# F5: Topology View — Implementation Plan

Date: 2026-06-11
Specs: ANIF-307 (SoT integration), design spec §16 F5
Backend dependency: B5 complete; SoT adapters are stubs — F5 adds the
minimal real slice: a file-backed local adapter + a topology read endpoint.
WCAG 2.1 AA required (enforced by Playwright/axe)

## Scope (design spec §16)

Network graph canvas, intent-status node colouring, interface detail
cards, intent overlay.

## Backend slice (TDD)

### Protocol additions (minimal, justified by F5 data needs)
- `Device.custom_fields: dict[str, str]` (default empty) — carries the
  write-back metadata (`intent_status`, `last_intent_id`,
  `intent_applied_at`) the UI colours by (ANIF-307 write-back contract)
- `SoTAdapter.list_interfaces(device) -> list[Interface]` — nothing
  currently returns Interface; detail cards need it
- Nautobot/NetBox/InfraHub stubs gain matching NotImplementedError stubs

### LocalSoTAdapter (`SOT_BACKEND=local`)
- Reads a YAML inventory (`SOT_LOCAL_INVENTORY`, sample committed at
  `simulation/sot/lab-inventory.yml`): site, devices (role, platform,
  primary_ip, tags, custom_fields, interfaces), connections
- Implements the full protocol including write-back: tag_device /
  tag_interface / tag_connection / set_custom_field mutate state and
  persist back to the YAML file (it IS the local source of truth)
- Unknown device/site → SoTAdapterError
- Sample lab: 2 spines, 3 leaves, 1 host; varied intent_status values
  (success / pending / failed / unset) so colouring is visible

### GET /topology endpoint (`sot/router.py`)
- `GET /topology?site=` (site optional → inventory default); X-API-Key
  auth; DI `get_sot_adapter` (overridable in tests)
- Response: `{site, devices: [{name, role, platform, primary_ip, tags,
  custom_fields, interfaces: [{name, ip_address, tags}]}],
  connections: [[a, b], ...]}`
- Unknown site → 404; adapter not configured → 503

Tests: adapter (load/get/list/topology/interfaces/write-back persists/
errors), router (auth 401, shape, 404), factory `local` branch.

## Frontend

```
src/anif_ui/src/
  api/topology.ts        ← types + getTopology(site?)
  lib/topologyLayout.ts  ← deterministic layered layout (group by role,
                            role-ordered rows, spread across width)
  components/TopologyGraph.tsx ← SVG canvas (role rows, links, nodes
                                  coloured by intent_status)
  pages/TopologyPage.tsx ← /topology (replaces placeholder)
```

### TopologyPage behaviour
- Loads topology; error/empty states as on other pages
- **Graph canvas**: SVG `role="img"` with descriptive aria-label; nodes
  coloured by `custom_fields.intent_status` (success/pending/failed/none);
  links from connections; node click selects device
- **Accessible device list**: parallel list of device buttons (keyboard
  path — selection never requires the SVG); selecting from either updates
  the detail panel
- **Interface detail cards**: selected device panel — role, platform,
  primary IP, tags, intent status Badge, `last_intent_id` link →
  /audit/:id timeline; per-interface cards (name, ip_address, tags)
- **Intent overlay legend**: colour → status mapping

## WCAG / tests
- axe audit: /topology with mocked /api/topology, node selected — 0 violations
- Live UAT: real backend with SOT_BACKEND=local; select node, see detail
  cards; verify colours match inventory intent_status values

## Task order
1. Backend TDD: failing adapter + router tests → implement → green
2. .env/.env.example: SOT_BACKEND=local + SOT_LOCAL_INVENTORY; sample inventory
3. api/topology.ts + layout lib + TopologyGraph + TopologyPage + route
4. axe audit — 0 violations
5. Gates (pytest/ruff/black/mypy, eslint/build) + live UAT
6. Architecture doc + commit
