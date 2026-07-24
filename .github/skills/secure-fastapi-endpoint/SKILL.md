---
name: secure-fastapi-endpoint
description: Implement or remediate a FastAPI endpoint with validated input, safe data access, explicit errors, and regression tests.
---

# Secure FastAPI endpoint workflow

Use this skill when adding an API endpoint or fixing an endpoint reported by CodeQL or
code review.

1. Read the route, response model, repository code, tests, and issue acceptance criteria.
2. Before changing any code, assess whether the change touches user-controlled input,
   data access, or error handling. If it does, treat this as a security-relevant change.
3. Identify every user-controlled value and constrain it with FastAPI/Pydantic types.
4. Keep database access parameterized. Do not use string formatting for SQL.
5. Remove dynamic execution such as `eval`, `exec`, or user-controlled shell commands.
6. Replace stack-trace responses with a stable public error and preserve diagnostic detail
   only through the project's safe logging pattern.
7. Add regression tests for the original exploit or failure mode and normal behavior.
8. Run `python scripts/validate.py` and the relevant targeted tests.
9. In the PR summary, explicitly answer: does this change have security implications? If
   yes, map each implication to its mitigation and any residual risk. If no, state why
   not. Do not omit this section even for small changes.

