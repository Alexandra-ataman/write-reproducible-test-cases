# Case content

Describe one user path from repeatable initial conditions to one target result.
Aim for one case per automated test. Follow the project's parameter and field conventions.
Add related variants to an existing case when possible. Preserve its valid checks, links, images, and conditions.

Use a new case for a separate path, branch, or result that cannot fit an existing case.
Missing coverage alone does not justify a separate case. Explain the boundary.
A component check alone does not justify a manual regression case.

Include the title, purpose, requirement sources, initial conditions, data, steps, and observable expected results.
Record the tested environment, build, variants, and total manual time estimate.
Include setup time and the estimate basis. Local time values use seconds.

Remove exploratory attempts and diagnostics from the case. Keep necessary setup and checks.
Use stable interface labels. Use coordinates or temporary values only when the test specifically examines them.
Make sure that each action follows from the previous state without hidden preparation.
