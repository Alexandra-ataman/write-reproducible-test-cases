# Project context

Find the case database and the code with automated tests.
Use this order:

1. The user's current instructions or earlier answers in this task.
2. The project of the specified existing case.
3. Saved task context or applicable project configuration.
4. Direct links in requirements, issues, or code changes.

Test source access. Let the user select between conflicting or ambiguous sources.
Do not assume that the current directory contains the product code.

Get only missing details:

> Where are the cases: TMS project, export, or folder?
> Which repository contains automated tests? Give its location and branch.
> State if either source does not exist.

Find test directories from configuration. Support separate product and E2E repositories.
Limit monorepository searches to the relevant project. Record the examined revision or client limitation.

Save choices and sources in `result.json.project_context` or the temporary task file `project-context.json`.
Reuse answers within the task. Current instructions override saved choices.
Do not create global project mappings without a separate request.

Use `none` for stated absence. Unknown sources are `unresolved`; sources without access are `inaccessible`.
Get an accessible copy when necessary. Continue independent work while the user answers.
Missing case access blocks a coverage conclusion. Missing code access blocks only the automation analysis.

Select an available browser tool for the target behavior. Follow user preferences and tool instructions.
Otherwise, get the tool and application URL from the user.
An earlier suitable report is also an option.
