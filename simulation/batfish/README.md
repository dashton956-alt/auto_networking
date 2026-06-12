# Batfish Network Config Analysis

This directory contains network configuration snapshots for static analysis with Batfish.

## What Batfish Does

Batfish analyses network configurations without running devices. It validates:
- BGP session correctness
- ACL reachability
- Route propagation
- Intent compliance

## Adding a Snapshot

Create a subdirectory with the snapshot name and add device configs:

```
simulation/batfish/
└── my-snapshot/
    ├── configs/
    │   ├── router-a.cfg
    │   └── router-b.cfg
    └── hosts/
        └── hosts.json
```

## Running Analysis

```bash
pip install pybatfish
python3 simulation/batfish/analyse.py my-snapshot
```
