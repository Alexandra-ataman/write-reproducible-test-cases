# Automated tests

For each new or updated draft, use the repositories from [project context](project-context.md).
Get missing locations from the user. If code is unavailable, use `blocked`; do not claim that tests are absent.

Find applicable test layers from configuration and nearby tests.
Search project directories by user action, domain entity, API, or component.
Read candidate assertions. Record exact references, covered behavior, and gaps.
A test filename alone does not prove coverage or a successful run.
Stop when relevant layers support a conclusion. Do not run tests merely to prove their presence.

Choose `add`, `update`, `covered`, `not_needed`, or `blocked`.
For `add` or `update`, identify a specific gap and test layer.
For `covered`, list the examined tests. Explain `not_needed` or `blocked`.
Do not write tests or create issues without a separate request.
Skip extra automation analysis for unchanged cases.
