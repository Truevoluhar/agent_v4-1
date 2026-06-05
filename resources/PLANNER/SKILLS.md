# Planner Skills

## Create Test Plan

Read the run context and inspect only the allowed URLs. Look for API documentation, common response formats, authentication requirements, allowed methods, and obvious health or version endpoints.

Create tests for:

- availability
- expected success responses
- missing parameters
- invalid input
- authentication problems
- unsupported methods
- response schema checks

Each test must be clear enough for the Executor to run without guessing.

Use `webservice_definition` tool to get information about webservice.

Save each test  as `./artifacts/test-plan-TESTNUMBER.json` via `write_file` tool. Replace TESTNUMBER with actual number. 

Do not include destructive tests unless the run context explicitly allows them.
