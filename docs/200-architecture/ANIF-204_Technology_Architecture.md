# ANIF-204: Technology Architecture

| Field        | Value                    |
|--------------|--------------------------|
| Doc ID       | ANIF-204                 |
| Series       | Architecture             |
| Version      | 0.1.0                    |
| Status       | Draft                    |
| Authors      | ANIF Working Group       |
| Reviewers    | —                        |
| Approved by  | —                        |
| Created      | 2026-04-07               |
| Last updated | 2026-04-07               |
| Replaces     | N/A                      |
| Related docs | ANIF-200, ANIF-203       |

---

## Abstract

This document defines the Technology Architecture for the Autonomous Networking & Infrastructure
Framework (ANIF). It specifies the normative technology stack, the rationale for each technology
choice, dependency management, container architecture, configuration management, logging
infrastructure, testing infrastructure, code quality standards, and API performance targets.
All ANIF implementations MUST conform to the technology choices and standards defined herein.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the authoritative technology choices for ANIF and the engineering
standards that govern code quality, testability, and operational readiness. It serves as the
definitive reference for contributors, reviewers, and CI/CD pipeline configuration.

### 1.2 Scope

This document covers:

- Normative technology stack with rationale and constraints
- Dependency management with version pinning
- Container architecture: Dockerfile and docker-compose design
- Configuration management and secrets handling
- Structured logging requirements
- Testing infrastructure and coverage targets
- Code quality standards and enforcement rules
- API performance targets by endpoint

### 1.3 Out of Scope

- Application module design (see ANIF-203)
- Security controls and RBAC (see ANIF-205)
- Network topology or infrastructure requirements
- CI/CD pipeline implementation details

### 1.4 Intended Audience

- Software engineers contributing to ANIF core
- DevOps engineers building ANIF deployment pipelines
- Code reviewers verifying standards compliance
- Plugin authors using ANIF as a platform

---

## 2. Normative References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- ANIF-000: Framework Constitution
- ANIF-200: Reference Architecture
- ANIF-203: Application Architecture
- Python Packaging Authority: pyproject.toml specification
- PEP 484: Type Hints
- PEP 257: Docstring Conventions
- Docker Engine Documentation
- pytest Documentation

---

## 3. Terms and Definitions

| Term             | Definition                                                                              |
|------------------|-----------------------------------------------------------------------------------------|
| Normative        | A requirement that MUST be met for conformance.                                         |
| Pin              | To specify an exact version or constrained version range in dependency declarations.    |
| Coverage         | The proportion of source code lines or branches exercised by the test suite.            |
| Structured Log   | A log entry serialised as JSON with defined fields, as opposed to free-form text.       |
| Bare except      | A Python `except:` clause with no exception type specified; prohibited in ANIF code.   |
| Enum             | A Python `enum.Enum` subclass used instead of raw string literals for typed constants. |

---

## 4. Technology Architecture

### 4.1 Normative Technology Stack

The following technology choices are normative. Implementations MUST use these technologies
for the components indicated. Substitutions require a formal architecture decision record.

| Technology         | Version Constraint | Role                                              | Satisfies Principle |
|--------------------|--------------------|---------------------------------------------------|---------------------|
| Python             | 3.11+              | Primary implementation language                   | P-08 Vendor Neutrality |
| FastAPI            | ≥ 0.110            | HTTP API framework                                | P-09 Incremental Adoption |
| Pydantic           | v2 (≥ 2.0)         | Data validation, schema definition                | P-03 Determinism    |
| pytest             | ≥ 8.0              | Test framework                                    | P-10 Test-First     |
| Docker             | ≥ 24.0             | Container runtime                                 | P-08 Vendor Neutrality |
| docker-compose     | ≥ 2.0 (Compose V2) | Local multi-service orchestration                 | P-09 Incremental Adoption |
| uvicorn            | ≥ 0.27             | ASGI server for FastAPI                           | —                   |
| structlog          | ≥ 24.0             | Structured logging                                | P-02 Auditability   |

#### 4.1.1 Python 3.11+

Python 3.11 is the minimum version. Rationale:

- Performance improvements (10–60% faster than 3.10 in benchmarks)
- Improved error messages aid debugging
- `tomllib` standard library module for `pyproject.toml` parsing
- `Self` type alias and `LiteralString` type from `typing`
- Required for Pydantic v2 performance optimisations

Implementations MUST NOT use Python 3.10 or earlier. The `python_requires` field in
`pyproject.toml` MUST be `">=3.11"`.

#### 4.1.2 FastAPI

FastAPI provides automatic OpenAPI schema generation, Pydantic integration, dependency
injection, and async support. Implementations MUST use FastAPI's dependency injection
system for shared resources (auth, store). Implementations MUST NOT use Flask, Django,
or other frameworks as the primary API layer.

#### 4.1.3 Pydantic v2

Pydantic v2 is significantly faster than v1 and provides strict validation mode. All
data entities defined in ANIF-202 MUST be implemented as Pydantic `BaseModel` subclasses.
Implementations MUST use `model_validate()` not `parse_obj()` (v1 API). The use of
`model_config = ConfigDict(strict=True)` is RECOMMENDED for entity models.

#### 4.1.4 pytest

All tests MUST be written using pytest. The `unittest` module MAY be used within pytest
test files but test discovery MUST use pytest. Test fixtures MUST be defined in `conftest.py`
files at appropriate scope levels.

### 4.2 Dependency Management

#### 4.2.1 pyproject.toml

All ANIF packages MUST use `pyproject.toml` as the single source of package metadata and
dependency declarations. `setup.py` and `requirements.txt` as primary dependency files are
PROHIBITED for new packages.

The `pyproject.toml` MUST include:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "anif"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.110,<1.0",
    "pydantic>=2.0,<3.0",
    "uvicorn[standard]>=0.27,<1.0",
    "structlog>=24.0,<25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",         # for FastAPI TestClient
    "ruff>=0.4",           # linter and formatter
    "mypy>=1.10",          # static type checker
]
```

#### 4.2.2 Version Pinning Strategy

- Direct dependencies MUST specify both a lower bound (`>=`) and an upper bound (`<`).
- The upper bound MUST be the next major version to prevent unintended breaking changes.
- Transitive dependencies MUST be resolved and pinned in a lock file (e.g., `uv.lock` or
  `pip-compile` generated `requirements.lock`) for reproducible builds.
- Lock files MUST be committed to the repository.
- Dependency updates MUST be a deliberate action, not an automatic side effect of `pip install`.

### 4.3 Container Architecture

#### 4.3.1 Dockerfile

The ANIF prototype Dockerfile MUST follow these requirements:

```dockerfile
# Required structure — illustrative, not normative line-for-line
FROM python:3.11-slim

# Non-root user is REQUIRED
RUN useradd --create-home --shell /bin/bash anif
WORKDIR /app
USER anif

# Separate dependency installation layer for caching
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Source code in a separate layer
COPY src/ ./src/
COPY schemas/ ./schemas/

# Health check is REQUIRED
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "anif.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Requirements for the Dockerfile:

1. MUST use an official Python slim base image; Alpine is DISCOURAGED due to glibc compatibility.
2. MUST run as a non-root user.
3. MUST include a `HEALTHCHECK` instruction.
4. MUST NOT include development dependencies in the production image layer.
5. MUST NOT copy `.env` files, credentials, or secrets into the image.
6. MUST expose only the API port (8000 by default).

#### 4.3.2 docker-compose.yml

The `docker-compose.yml` MUST define the prototype deployment. Production multi-service
deployment SHOULD use a separate `docker-compose.prod.yml` or Kubernetes manifests.

```yaml
# Required structure — illustrative
version: "3.9"

services:
  anif:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANIF_ENV=development
      - ANIF_LOG_LEVEL=INFO
      # Secrets via environment variables; never hardcoded
      - ANIF_API_KEY=${ANIF_API_KEY}
    volumes:
      # Mount schemas directory for development hot-reload of policies
      - ./schemas:/app/schemas:ro
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
```

The `docker-compose.yml` MUST NOT contain secret values. All secrets MUST be passed via
environment variables sourced from a `.env` file that is listed in `.gitignore`.

### 4.4 Configuration Management

#### 4.4.1 Configuration Sources (Priority Order)

1. Environment variables (highest priority)
2. `.env` file loaded at startup (development only)
3. Default values in Pydantic settings model (lowest priority)

#### 4.4.2 Pydantic Settings

All application configuration MUST be defined in a Pydantic settings model:

```python
# src/anif/core/config.py (illustrative)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """ANIF application configuration.

    All values are loaded from environment variables. Prefix: ANIF_
    """
    env: str = "development"
    log_level: str = "INFO"
    api_key: str        # No default — REQUIRED in production
    risk_threshold_auto: float = 0.3
    risk_threshold_block: float = 0.8
    ticket_expiry_minutes: int = 15
    plugin_paths: list[str] = []

    model_config = ConfigDict(env_prefix="ANIF_")
```

#### 4.4.3 Secrets Management Rules

1. Secrets MUST NOT appear in source code, YAML schemas, or pyproject.toml.
2. Secrets MUST NOT be committed to the repository under any circumstances.
3. `.env` files containing secrets MUST be listed in `.gitignore`.
4. In production, secrets MUST be injected via the container orchestrator's secret mechanism
   (e.g., Docker Secrets, Kubernetes Secrets, Vault).
5. Log output MUST NOT include secret values; the logging framework MUST redact known secret
   field names.

### 4.5 Logging Infrastructure

#### 4.5.1 Structured Logging Requirements

All ANIF code MUST use structured logging. The following rules are normative:

1. `print()` statements are PROHIBITED in all non-test production code.
2. All logging MUST use the `structlog` library or the standard `logging` module with a
   JSON formatter. Direct use of `print()` for diagnostic output is PROHIBITED.
3. Every log entry MUST include: `timestamp`, `level`, `logger`, `trace_id` (when available),
   `event` (message string).
4. Log levels MUST be used consistently:
   - `DEBUG`: Internal state useful for development debugging only
   - `INFO`: Normal operational events (startup, plugin registration, pipeline stage entry)
   - `WARNING`: Recoverable conditions that may indicate misconfiguration or degraded state
   - `ERROR`: Failures that prevent a pipeline stage from completing
   - `CRITICAL`: Conditions requiring immediate human intervention
5. Log entries MUST NOT contain: secrets, credentials, API keys, PII, raw stack traces
   in production mode.

#### 4.5.2 Required Log Events

The following events MUST be logged at the indicated level:

| Event                              | Level    | Required Fields                                     |
|------------------------------------|----------|-----------------------------------------------------|
| Application startup                | INFO     | version, env, plugin_count                          |
| Plugin registered                  | INFO     | plugin_name, plugin_version, capabilities           |
| Plugin registration failed         | ERROR    | plugin_name, reason                                 |
| Intent received                    | INFO     | trace_id, action, requestor_role                    |
| Intent validation failed           | WARNING  | trace_id, validation_errors                         |
| Policy conflict detected           | WARNING  | trace_id, conflict_count                            |
| Risk score computed                | INFO     | trace_id, score, trust_level                        |
| Governance mode assigned           | INFO     | trace_id, mode, reason                              |
| Governance blocked                 | WARNING  | trace_id, reason                                    |
| Action executed                    | INFO     | trace_id, action_type, adapter, status              |
| Action execution failed            | ERROR    | trace_id, action_type, error_code                   |
| Rollback executed                  | WARNING  | trace_id, action_type, original_execution_id        |
| Approval ticket expired            | WARNING  | ticket_id, trace_id                                 |

### 4.6 Testing Infrastructure

#### 4.6.1 Test Structure

Tests MUST be organised in the following directory structure:

```
tests/
├── conftest.py          # Root fixtures: app client, in-memory store, common mocks
├── unit/
│   ├── intent/          # Unit tests for each module
│   ├── policy/
│   ├── risk/
│   ├── decision/
│   ├── actions/
│   ├── governance/
│   └── audit/
├── integration/
│   ├── test_pipeline.py # End-to-end pipeline tests via HTTP
│   ├── test_orchestrate.py
│   └── test_rollback.py
└── fixtures/
    ├── intents.yaml     # Sample intent payloads
    ├── policies.yaml    # Sample policy sets for testing
    └── scenarios.yaml   # Named test scenarios for parametrised tests
```

#### 4.6.2 Testing Requirements

1. The test suite MUST be runnable with `pytest` from the repository root.
2. All test fixtures MUST be deterministic. Tests MUST NOT rely on network calls to external
   systems; all external dependencies MUST be mocked.
3. The mock adapter (`MockNetworkAdapter`) MUST be used in all tests; real network adapters
   MUST NOT be invoked in unit or integration tests.
4. Code coverage MUST be measured with `pytest-cov` on every CI run.
5. The overall code coverage MUST be ≥ 80%. Coverage MUST NOT be excluded except for
   explicitly justified cases (e.g., `# pragma: no cover` with a comment explaining why).
6. Integration tests MUST use FastAPI's `TestClient` (via `httpx`) to call endpoints through
   the full HTTP stack.
7. Every API endpoint MUST have at least one integration test covering the happy path and
   at least one test covering a failure mode.
8. Parametrised tests using `pytest.mark.parametrize` are RECOMMENDED for testing multiple
   input combinations.
9. Tests MUST be independent; each test MUST set up and tear down its own state.

#### 4.6.3 Running Tests

```bash
# Run all tests with coverage
pytest --cov=src/anif --cov-report=term-missing

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v
```

### 4.7 Code Quality Standards

The following standards are normative for all code in `src/anif/`. Violations MUST be
caught by linting in CI and MUST block merge.

#### 4.7.1 Docstrings

Every public function, method, and class MUST have a docstring. Docstrings MUST conform to
the Google docstring style (as supported by most Python docstring linters).

```python
def score_risk(intent: Intent, policy_result: PolicyResult) -> RiskScore:
    """Compute a risk score for the proposed intent.

    Args:
        intent: The validated intent object.
        policy_result: The policy evaluation result for this intent.

    Returns:
        A RiskScore object with score, factors, and trust level.

    Raises:
        RiskScoringError: If the intent action type is not scoreable.
    """
```

#### 4.7.2 Type Hints

All function signatures MUST include type hints for parameters and return values. Use of
`Any` type is DISCOURAGED and MUST be justified with a comment. All type hints MUST pass
`mypy --strict` without suppression.

#### 4.7.3 Function Length

Individual functions MUST NOT exceed 40 lines (excluding docstrings and blank lines).
Functions approaching this limit SHOULD be refactored into smaller, focused functions.

#### 4.7.4 File Length

Source files MUST NOT exceed 300 lines. Files approaching this limit SHOULD be split into
focused modules. Test files are exempt from this limit but SHOULD follow the same spirit.

#### 4.7.5 Exception Handling

Bare `except:` clauses are PROHIBITED. All `except` clauses MUST specify at least one
exception type. Catching `Exception` is DISCOURAGED unless the intent is to catch-and-log
at a top-level handler.

```python
# PROHIBITED
try:
    execute_action()
except:
    pass

# REQUIRED
try:
    execute_action()
except ExecutionError as exc:
    logger.error("action_execution_failed", error=str(exc), trace_id=trace_id)
    raise
```

#### 4.7.6 String Constants

Hardcoded string literals used as identifiers, status values, or action names are PROHIBITED.
All such values MUST be defined as Python `enum.Enum` members and referenced by name.

```python
# PROHIBITED
if action == "reroute_traffic":
    ...

# REQUIRED
class ActionType(str, Enum):
    REROUTE_TRAFFIC = "reroute_traffic"
    ...

if action == ActionType.REROUTE_TRAFFIC:
    ...
```

#### 4.7.7 Linting and Formatting

`ruff` MUST be used for linting and formatting. The `ruff` configuration MUST be defined
in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
# B = flake8-bugbear, C4 = flake8-comprehensions, SIM = flake8-simplify
```

`mypy` MUST be configured in `pyproject.toml` and run in CI:

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
```

### 4.8 Performance Targets

The following response time targets MUST be met under normal load conditions (single concurrent
request, prototype deployment). These targets apply to the 99th percentile (P99) latency.

| Endpoint                        | P99 Target   | Notes                                                  |
|---------------------------------|--------------|--------------------------------------------------------|
| `POST /validate-intent`         | < 50ms       | Pydantic validation only; no external calls            |
| `POST /evaluate-policy`         | < 100ms      | Policy loading from memory; no DB calls in prototype   |
| `POST /score-risk`              | < 50ms       | Deterministic computation; no external calls           |
| `POST /decide`                  | < 50ms       | Decision selection from bounded set; no external calls |
| `POST /governance/check`        | < 50ms       | RBAC + mode lookup; no DB calls                        |
| `POST /execute` (mock adapter)  | < 200ms      | Mock adapter; real adapter latency varies by vendor    |
| `POST /orchestrate` (dry_run)   | < 500ms      | Full pipeline except execution                         |
| `POST /orchestrate` (live)      | < 1000ms     | Full pipeline including mock execution                 |
| `GET /audit/{intent_id}`        | < 100ms      | In-memory lookup in prototype                          |
| `GET /audit/{intent_id}/why`    | < 100ms      | In-memory; summary construction                        |
| `GET /feedback/analysis`        | < 200ms      | In-memory aggregation                                  |

Performance targets for production deployments with persistent stores SHOULD be validated
separately as latency characteristics differ from the in-memory prototype.

---

## 5. Conformance Requirements

1. Implementations MUST use Python 3.11 or later.
2. Implementations MUST use FastAPI for the HTTP API layer.
3. All data entities MUST be implemented using Pydantic v2 `BaseModel`.
4. `print()` statements MUST NOT appear in production source code.
5. All production code MUST use structured logging as defined in Section 4.5.
6. Code coverage MUST be ≥ 80% as measured by `pytest-cov`.
7. All function signatures MUST include type hints.
8. All public functions and classes MUST have docstrings.
9. Functions MUST NOT exceed 40 lines; files MUST NOT exceed 300 lines.
10. Bare `except:` clauses are PROHIBITED.
11. String constants used as identifiers MUST be defined as enums.
12. API endpoints MUST meet the performance targets defined in Section 4.8 in the prototype.

---

## 6. Security Considerations

- Secrets MUST NOT appear in source code, environment files committed to version control,
  or log output.
- The Docker container MUST run as a non-root user.
- Dependency versions MUST be pinned to prevent supply chain injection via unexpected updates.
- The `ruff` linter includes bugbear rules (B) that catch common security-adjacent issues
  (e.g., mutable default arguments, assert statements in production code).
- All dependencies SHOULD be audited with `pip-audit` or equivalent on every CI run.

---

## 7. Operational Considerations

- CI pipelines MUST run `ruff check`, `mypy`, and `pytest --cov` on every pull request.
- Coverage MUST NOT decrease between commits; CI MUST fail if coverage drops below 80%.
- Docker images MUST be built and health-checked in CI before merging.
- The Makefile MUST provide targets: `make lint`, `make typecheck`, `make test`, `make build`,
  `make run`, `make clean`.
- Log aggregation in production SHOULD collect structured JSON logs from all containers and
  index them by `trace_id` for efficient pipeline-level log queries.

---

## Appendix A: Examples

### A.1 Makefile Targets

```makefile
.PHONY: lint typecheck test build run clean

lint:
	ruff check src/ tests/

typecheck:
	mypy src/

test:
	pytest --cov=src/anif --cov-report=term-missing --cov-fail-under=80

build:
	docker compose build

run:
	docker compose up

clean:
	docker compose down --volumes
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
```

### A.2 Structured Log Entry Example

```json
{
  "timestamp": "2026-04-07T14:30:00.045Z",
  "level": "info",
  "logger": "anif.intent",
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event": "intent_validated",
  "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "action": "reroute_traffic",
  "requestor_role": "automation_agent",
  "latency_ms": 12
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Summary                  |
|---------|------------|--------------------|--------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft            |
