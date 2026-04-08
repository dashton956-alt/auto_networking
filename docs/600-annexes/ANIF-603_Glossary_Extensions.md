# ANIF-603: Glossary Extensions

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-603                                           |
| Series       | Annex                                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-003, ANIF-300, ANIF-400                       |

---

## Abstract

This document extends the core ANIF glossary (ANIF-003) with domain-specific terminology covering networking, telecommunications, cloud infrastructure, and ANIF-specific technical terms. It also provides a comprehensive acronym and abbreviation table. Terms defined here are supplementary to ANIF-003; in the event of a conflict, ANIF-003 takes precedence.

---

## 1. Introduction

### 1.1 Purpose

ANIF-003 defines terms used normatively across the framework. This document adds domain-specific vocabulary for implementers working in networking, telco, and cloud contexts, and for readers requiring disambiguation of technical acronyms.

### 1.2 Scope

Extended terms covering: networking protocols and concepts, telecommunications network domains, cloud infrastructure, and ANIF-specific implementation vocabulary.

### 1.3 Out of scope

General IT terms, programming language concepts, and terms already defined in ANIF-003.

### 1.4 Intended audience

Engineers and architects implementing ANIF in networking, telco, or cloud environments.

---

## 2. Normative references

- ANIF-003 — Terms and Definitions (core glossary)
- RFC 2119 — Key words for use in RFCs

---

## 3. Extended Terms and Definitions

### 3.1 Networking Terms

| Term | Definition |
|---|---|
| BGP | Border Gateway Protocol — the routing protocol of the internet; manages how packets are routed between autonomous systems |
| OSPF | Open Shortest Path First — a link-state routing protocol used within an autonomous system to find the shortest path between nodes |
| MPLS | Multiprotocol Label Switching — a routing technique that directs data using labels rather than IP addresses; used for traffic engineering |
| ISIS | Intermediate System to Intermediate System — a link-state routing protocol used in carrier networks and data centres |
| ECMP | Equal-Cost Multi-Path — a routing strategy where multiple paths of equal cost are used simultaneously for load balancing |
| SDN | Software-Defined Networking — an architecture that separates the control plane from the data plane, enabling programmatic network management |
| NFV | Network Function Virtualisation — the replacement of dedicated network hardware appliances with software running on commodity hardware |
| SD-WAN | Software-Defined Wide Area Network — SDN applied to WAN connections, enabling centralised policy-based management |
| Zero Trust | A security model that assumes no implicit trust based on network location; every request must be authenticated and authorised |
| ZTNA | Zero Trust Network Access — a security framework implementing Zero Trust principles for application access |
| Microsegmentation | Dividing a network into small, isolated segments to limit lateral movement in the event of a breach |
| East-West Traffic | Traffic flowing laterally between services within a data centre or network, as opposed to North-South traffic entering/leaving |
| North-South Traffic | Traffic flowing into or out of a network boundary (client to server, external to internal) |
| ACL | Access Control List — a set of rules controlling what traffic is permitted to enter or leave a network segment |
| QoS | Quality of Service — mechanisms to control traffic prioritisation, bandwidth allocation, and latency guarantees |
| Traffic Engineering | The process of optimising network performance by controlling traffic paths; often implemented via MPLS TE or SR |
| Segment Routing | A source routing architecture where the path is encoded as a sequence of instructions (segments) in the packet header |
| VxLAN | Virtual Extensible LAN — a network virtualisation technology encapsulating Layer 2 frames within UDP packets for overlay networks |
| Overlay Network | A virtual network built on top of physical infrastructure; provides logical isolation between tenants or workloads |
| Underlay Network | The physical infrastructure on which overlay networks are built |
| VLAN | Virtual Local Area Network — a logical partition of a physical network, isolating broadcast domains |
| EVPN | Ethernet VPN — a standards-based control plane for building scalable Layer 2 and Layer 3 VPN services |
| BGP Flowspec | An extension to BGP for distributing traffic flow specifications; used for DDoS mitigation and traffic steering |

### 3.2 Telecommunications Terms

| Term | Definition |
|---|---|
| RAN | Radio Access Network — the part of a mobile network that connects end-user devices to the core network via radio spectrum |
| Core Network | The central component of a telecommunications network providing authentication, routing, and session management |
| Transport Network | The network layer (IP/MPLS, optical) that carries traffic between RAN sites, core nodes, and data centres |
| Network Slice | An end-to-end logical network with isolated resources and specific SLA characteristics, created over shared physical infrastructure |
| 5G NR | 5G New Radio — the air interface standard for 5G networks defined by 3GPP |
| gNodeB (gNB) | A 5G base station providing the radio interface between UEs and the 5G Core |
| eNodeB (eNB) | A 4G LTE base station; connects User Equipment (UE) to the Evolved Packet Core (EPC) |
| UPF | User Plane Function — the 5G Core network function responsible for packet routing and forwarding |
| AMF | Access and Mobility Management Function — the 5G Core function handling device registration, authentication, and mobility |
| SMF | Session Management Function — the 5G Core function managing PDU sessions |
| NSSF | Network Slice Selection Function — the 5G Core function that selects appropriate network slices for a given request |
| VNF | Virtualised Network Function — a software implementation of a network function running on a virtual machine |
| CNF | Cloud-native Network Function — a network function implemented as containerised microservices (pods) |
| NFVI | Network Function Virtualisation Infrastructure — compute, storage, and network resources hosting VNFs |
| MANO | Management and Orchestration — the NFV framework for managing VNF lifecycle and orchestrating network services |
| SON | Self-Organising Network — automated capabilities in RAN for self-configuration, self-optimisation, and self-healing |
| S-NSSAI | Single Network Slice Selection Assistance Information — a 5G identifier for a specific network slice |
| PLMN | Public Land Mobile Network — a network established and operated by an organisation for the purpose of providing mobile services |
| IMS | IP Multimedia Subsystem — a framework for delivering multimedia communications services over IP networks |
| OSS/BSS | Operations Support Systems / Business Support Systems — the software platforms telcos use for network management (OSS) and customer-facing services (BSS) |

### 3.3 Cloud Infrastructure Terms

| Term | Definition |
|---|---|
| VPC | Virtual Private Cloud — a logically isolated section of a cloud provider's network dedicated to a single tenant |
| Security Group | A virtual firewall controlling inbound and outbound traffic for cloud resources within a VPC |
| Load Balancer | A service that distributes incoming network traffic across multiple backend instances |
| Auto-scaling | The automatic adjustment of compute capacity based on demand, scaling out (more instances) or in (fewer instances) |
| Availability Zone | An isolated location within a cloud region, with independent power, cooling, and networking |
| Region | A geographical area containing multiple Availability Zones; data may be restricted to a region for compliance reasons |
| Service Mesh | An infrastructure layer handling service-to-service communication, providing traffic management, observability, and security |
| Ingress Controller | A Kubernetes component managing external access to services within a cluster |
| Egress | Traffic leaving a network boundary (cloud VPC, data centre, cluster) |
| Transit Gateway | A network transit hub connecting VPCs and on-premises networks through a central routing construct |
| Peering | A direct network connection between two cloud VPCs or networks, enabling private communication without traversing the public internet |
| IAM | Identity and Access Management — cloud service controlling who can access what resources under what conditions |
| Cloud-native | Applications designed to exploit cloud capabilities: containerised, dynamically orchestrated, microservices-based |
| Terraform | An infrastructure-as-code tool for declaring and provisioning cloud resources |
| Kubernetes | An open-source container orchestration platform for automating deployment, scaling, and management of containerised applications |

### 3.4 ANIF-Specific Technical Terms

| Term | Definition |
|---|---|
| Policy Condition Syntax | The grammar used to express policy rules in ANIF: `field_path:operator:value`. Operators: equals, not_equals, greater_than, less_than, contains, not_contains, in_list, not_in_list |
| Risk Factor | An individual contributor to the aggregate risk score. Each factor has a weight (point value) and a source (which part of the intent or context triggered it) |
| Safety Budget | The maximum aggregate risk score permitted for autonomous execution (the block threshold). Defined per environment in the threshold set |
| Threshold Set | The pair of thresholds (warn, block) applied during risk scoring. Two sets: prod (warn=40, block=70) and non_prod (warn=60, block=85) |
| Approval Ticket | A governance artefact created when an action requires manual_review. Fields: ticket_id, intent_id, decision_summary, risk_score, requested_by, created_at, expires_at (15 min), status |
| Execution Adapter | The component implementing the interface between the ANIF action executor and a specific vendor or platform API |
| Mock Adapter | A test-only execution adapter that simulates real adapter behaviour without contacting actual network devices |
| Canonical State | The authoritative, merged representation of network topology derived from multiple source-of-truth systems (NetBox, CMDB, cloud APIs) |
| Source Freshness Score | A metric indicating how recently a data source was successfully read; stale sources increase risk score |
| Reasoning Chain | An ordered list of decision steps produced by each pipeline stage. Each step records what was evaluated, the decision made, and why |
| Dry Run | A pipeline invocation mode (`dry_run=true`) that runs all evaluation stages but skips governance approval and action execution |
| Intent Hash | A deterministic hash of an intent object, used in mock adapters to produce consistent simulated outcomes in tests |
| Trace ID | A UUID assigned to each API request and propagated through all pipeline stages and log entries for end-to-end correlation |
| Write-Before-Return | The ANIF requirement that audit records MUST be written and confirmed before the API response is returned to the caller |
| Bounded Action Selection | The constraint that the decision engine MUST only select from the 4 predefined action types; free-form action generation is prohibited |

---

## 4. Acronym and Abbreviation Table

| Acronym | Expansion |
|---|---|
| ABAC | Attribute-Based Access Control |
| ADM | Architecture Development Method (TOGAF) |
| AMF | Access and Mobility Management Function |
| AN | Autonomous Networks (TMForum) |
| ANIF | Autonomous Networking and Infrastructure Framework |
| API | Application Programming Interface |
| BGP | Border Gateway Protocol |
| BSS | Business Support Systems |
| CMDB | Configuration Management Database |
| CNF | Cloud-native Network Function |
| CSF | Cybersecurity Framework (NIST) |
| DDoS | Distributed Denial of Service |
| ECMP | Equal-Cost Multi-Path |
| EPC | Evolved Packet Core (4G) |
| ETSI | European Telecommunications Standards Institute |
| EVPN | Ethernet VPN |
| gNMI | gRPC Network Management Interface |
| HTTP | Hypertext Transfer Protocol |
| IAM | Identity and Access Management |
| IETF | Internet Engineering Task Force |
| IMS | IP Multimedia Subsystem |
| ISO | International Organisation for Standardisation |
| JSON | JavaScript Object Notation |
| KPI | Key Performance Indicator |
| MANO | Management and Orchestration |
| MPLS | Multiprotocol Label Switching |
| MTTR | Mean Time to Repair/Recover |
| NFVI | Network Function Virtualisation Infrastructure |
| NFV | Network Function Virtualisation |
| NIST | National Institute of Standards and Technology |
| NOC | Network Operations Centre |
| NSSF | Network Slice Selection Function |
| OSS | Operations Support Systems |
| OSPF | Open Shortest Path First |
| PCI-DSS | Payment Card Industry Data Security Standard |
| PLMN | Public Land Mobile Network |
| QoS | Quality of Service |
| RACI | Responsible, Accountable, Consulted, Informed |
| RAN | Radio Access Network |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| RFC | Request for Comments |
| RESTCONF | REST-based protocol for NETCONF datastores |
| SD-WAN | Software-Defined Wide Area Network |
| SDN | Software-Defined Networking |
| SLA | Service Level Agreement |
| SLO | Service Level Objective |
| SMF | Session Management Function |
| S-NSSAI | Single Network Slice Selection Assistance Information |
| SON | Self-Organising Network |
| TOGAF | The Open Group Architecture Framework |
| UPF | User Plane Function |
| UUID | Universally Unique Identifier |
| VLAN | Virtual Local Area Network |
| VNF | Virtualised Network Function |
| VPC | Virtual Private Cloud |
| VxLAN | Virtual Extensible LAN |
| YAML | YAML Ain't Markup Language |
| ZSM | Zero-touch network and Service Management (ETSI) |
| ZTNA | Zero Trust Network Access |

---

## 5. Conformance Requirements

No conformance requirements apply to this annex. It is informative.

---

## 6. Security Considerations

None specific to this glossary document.

---

## 7. Operational Considerations

This document SHOULD be updated whenever new domain-specific terms are introduced in normative ANIF documents. Proposed additions SHOULD be submitted as issues to the ANIF issue tracker referencing the source document.

---

## Appendix A: Contributing New Terms

To propose a new term for this glossary:

1. Open an issue in the ANIF repository with label `glossary`
2. Provide: term, definition, source document or standard, and the ANIF documents where it appears
3. The working group reviews and assigns the term to ANIF-003 (if normative) or ANIF-603 (if domain-specific)

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
