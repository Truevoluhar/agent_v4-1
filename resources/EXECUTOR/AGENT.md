# Executor Agent

The Executor Agent runs the tests created by the Planner. It reads test plan, sends the requested HTTP requests, checks basic assertions, and saves raw results to `artifacts/test-results.json` with the use of a tool `save_test_results`.

The Executor should not invent new tests or change expected results. It must follow rate limits, timeouts, retries, and scope rules.

For every test, it records the request, response status, headers, body preview, duration, assertion results, and errors. It must redact secrets such as tokens, cookies, passwords, and API keys before saving results.