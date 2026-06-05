# Orchestrator Skills

## Manage Test Run

Read the user request and identify the target URLs, allowed hosts, test depth, authentication needs, and safety limits.

Create a simple run context containing:

- target URLs
- allowed hosts
- artifact paths
- rate limit
- timeout
- destructive testing policy

Then call the agents in order:

1. Planner creates `test-plan.json`.
2. Executor creates `test-results.json`.
3. Validator creates `validation-report.md`.

Before moving to the next phase, confirm that the previous output file exists and is usable. Stop if testing would go outside the allowed scope.
