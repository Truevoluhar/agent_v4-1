# Executor Skills

## Run Tests

Load test cases via tool `load_test_cases` and validate that every test is in scope. Skip tests that are unsafe or destructive without permission.
You have the ability to meaningfully provide test execution, that means obtaining valid authentication request parameters, such as usernames, passwords, tokens, etc.
You have the ability to replace placeholder values in test cases with real values, obtained from previous endpoint tests or other sources.
Here is your workflow:
1. Use tool `load_test_cases`.
2. For every test case use tool `test_endpoint`. Replace request parameter placeholders if necessary.
3. After you have tested every endpoint, use tool `save_test_results` and provide test results information, like did test pass, fail, etc.