# Output and final review

Use the requested case language and project format. Save local Markdown by default.
Use available TMS fields only for authorized external changes.

## Case content

Include:

- Title, purpose, requirement sources, and the existing case link for an update.
- Repeatable initial conditions, accounts, data, settings, and mock setup when applicable.
- Numbered actions with an observable expected result for every step.
- Required images beside the related condition or expected result.
- Checked environment, build, date, client, and variants.
- Total manual time estimate, including setup, with its unit and basis.

Keep exploratory attempts and diagnostics in the execution log. Preserve valid checks when updating a case.

## Final review

Before you deliver each case:

1. Compare the written initial conditions with the actual setup. Remove hidden dependencies on a previous run.
2. Match every action and expected result to execution evidence for the relevant version and environment.
3. Repeat changed steps when their evidence is insufficient. Keep requirement expectations when the product fails.
4. Open the execution report and required images. Make sure that files exist, contain useful evidence, and have working links.
5. Confirm the coverage decision. Read covering cases in full; justify updates and new cases.
6. Record automated coverage, exact test references, gaps, and the next action, or explain unavailable code access.
7. For TMS changes, independently read saved content, status, time units, source links, and attachments.

Use `draft` only when the target steps pass, initial conditions are repeatable, and all necessary evidence is available.
Use `blocked` for an incomplete or failed target check. Explain what is necessary to continue.
Use `preview` only for explicitly requested, untested early cases. Keep them outside the regression database.
Use `unchanged` when existing coverage is sufficient or the check has no regression value.

Limit conclusions to the observed environment and variants. State all mocks and what they do not verify.
The case text and its own report are not proof of execution. Use actual observations and artifacts.

## Short report

List each scenario, the decision to create/update/leave unchanged, its status, and a case link or file.
State whether a new run occurred. Otherwise, link the earlier report and explain its applicability.
Link evidence and explain limits, blockers, coverage decisions, and automation recommendations.
Record the selected case project, repositories, search scope, and the sources of those choices.
For external writes, distinguish saved-and-checked cases from local proposals and unconfirmed operations.
