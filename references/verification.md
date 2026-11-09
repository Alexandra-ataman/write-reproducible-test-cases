# Confirm the path

Use an earlier report with successful tests of the current requirements and build.
Read its actions and results. Examine relevant images. Record its date, build, environment, and limits.
Use `existing_report` with `new_run: false`. A success label alone is insufficient.

For a new run, identify the missing condition, action, result, or variant.
Select a suitable tool through [project context](project-context.md). [Playwright CLI](playwright-cli.md) is one option.

1. Record the application URL, build, date, client, and checked variants.
2. Prepare account, data, permissions, and settings. Record repeatable setup without saved secrets.
3. Perform the actions. Examine observable results. Save an execution log linked to case steps.
4. Capture required images. Examine the necessary effect. An outgoing request alone does not prove server persistence.
5. Compare the final case with the actual path. Repeat changed parts without sufficient test evidence.

Restore the initial state before a repeat. Include temporary data limits in the conditions.
Test device-specific behavior in the target environment. Record all mocks and their limits.
Do not report a mocked check as proof of the full integration.

Record defects and unconfirmed parts as blockers.
Keep the action log to explain transitions between screenshots.
An independent repeat can test the written instructions. It is optional.
Stop after a successful test of the missing part.
