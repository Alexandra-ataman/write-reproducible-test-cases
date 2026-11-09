---
name: write-reproducible-test-cases
description: >-
  Write and update regression test cases from requirements and tested user actions.
  Examine existing cases, repeat the required steps, and record evidence.
  Use for case authoring and reproducibility checks. Prepare untested previews only on request.
  Save local Markdown by default. Use an available TMS client for authorized changes.
---

# Write Reproducible Test Cases

Set expectations from requirements. Test the steps in the application. Follow the project format and requested case language.

## Procedure

1. Read requirements and clarifications. Use code or designs for specific gaps.
2. Read [project context](references/project-context.md). Find the case project, code repositories, and a suitable browser tool.
   Get missing details from the user. Keep the answers for this task.
3. Read [coverage](references/coverage.md). Examine existing cases before you propose changes.
   Prefer no change, then an update. Justify each new case as a separate user path.
4. Read [authoring](references/authoring.md). Show proposed changes, reasons, evidence, images, and time estimates.
   Continue authorized work without another approval request.
5. Read [verification](references/verification.md). Use a suitable earlier report or repeat the missing part of the path.
   Examine conditions, actions, and results. Apply [media rules](references/media.md) when necessary.
6. Write the tested path with requirement-based expectations.
   Record product defects separately. Keep unconfirmed cases outside the regression database.
7. Read [integration](references/integration.md) before an authorized TMS change. Read the saved result after each change.
   For local work, save case proposals. Do not describe them as TMS changes.
8. Examine [automation coverage](references/automation.md) for each new or updated draft.
9. Use the [output contract](references/output.md) to prepare `result.json`. Run:

   ```bash
   python3 <skill-dir>/scripts/finalize_cases.py <result-dir>/result.json
   ```

10. Read the output as a tester. Examine instructions, links, and saved fields.
    Correct contract errors before you report success.

## Results and limits

Use `draft` only when all steps pass and necessary media exist.
Use `blocked` for an incomplete check. State what is necessary.
Use `preview` only for requested, untested drafts.
Use `unchanged` for sufficient coverage or a check without regression value.

Limit each conclusion to the tested build, environment, data, and variants.
Record mocks and their limits.
The helper examines structure and files. The agent must examine their content and actual application behavior.

Keep external changes within authorization, including publication, deletion, archiving, and project settings.
