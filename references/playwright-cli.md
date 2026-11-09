# Example: Playwright CLI

Use an installed [Playwright CLI](https://github.com/microsoft/playwright-cli) with a coding agent.
Read its help and [network documentation](https://playwright.dev/agent-cli/commands/network-routing).
Use `route` to replace responses.

This example tests a UI error state with a mock HTTP 503 response.
Use the authorized application URL and API pattern in a separate session.
Run commands in the result directory.

```bash
playwright-cli -s=case-check open http://localhost:3000 --headed
playwright-cli -s=case-check route "**/api/items" --status=503
playwright-cli -s=case-check reload
playwright-cli -s=case-check snapshot
playwright-cli -s=case-check screenshot --filename=evidence/items-error.png
playwright-cli -s=case-check unroute "**/api/items"
playwright-cli -s=case-check reload
playwright-cli -s=case-check snapshot
```

After each snapshot, examine the interface state against the requirements.
Log observations. Record the mock pattern, response, setup, and removal in the case.
Install routes before requests. Repeat startup actions after setup when necessary.
Remove routes after the check, including after a failure.

This test shows the UI response to the mock. Test the real service when integration behavior matters.
Select another tool only if its API supports the necessary operations.
Make sure that the tool supports network interception.
