You are an expert in policy-as-code systems.

Task:
Generate a policy evaluation engine.

Inputs:
- Intent object
- Policy definitions

Requirements:
- Evaluate constraints BEFORE execution
- Return:
  - pass/fail
  - violated policies
- Deterministic logic only (no AI decisions)

Output:
- Python module
- Clear evaluation flow
- Unit-testable functions