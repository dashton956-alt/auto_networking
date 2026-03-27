You are a senior backend engineer.

Task:
Generate a Python FastAPI service that validates network intent against a JSON schema.

Context:
- Input: intent JSON
- Validation: strict schema + custom rules
- Output: validation result with errors

Constraints:
- Deterministic behavior only
- No assumptions outside schema
- Include:
  - API endpoint (/validate-intent)
  - Pydantic models
  - Error handling

Output:
- Production-ready Python code