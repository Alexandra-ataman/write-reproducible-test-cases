# Output contract

Save `result.json` in a separate directory. Use the fields below to record the actual result of the task.

## Project and coverage

`mode`: `verified` for normal work; `preview` for requested early drafts. Check each case status for its outcome.

`project_context.case_project`: `status`, `location` (URL/path or null), `source`, `reason`.
`project_context.automation_repositories`: `status`, `repositories`, `source`, `reason`.
Each repository has `location`, search `scope`, and examined `revision` or a stated revision limit.

Context states: `resolved`, `none`, `unresolved`, `inaccessible`.
Use `none` only for stated absence, with null case location or an empty repository list.
Resolved sources need locations; automation needs a nonempty repository list.

`coverage` has `status`, `scope`, `queries`, `read_cases`, `reason`.
Each read case has `ref` and a content `comparison`.

| Coverage status | Required basis |
|---|---|
| `complete` | Resolved project; at least two distinct queries; relevant candidates read in full |
| `targeted` | Resolved project; editorial update of a fully read case |
| `not_applicable` | Confirmed absence of a case database |
| `unavailable` | Unknown, inaccessible, or incomplete source |

## Cases

Each case has unique lowercase-hyphenated `id`, `title`, `action`, `status`, `reason`, and nonempty `sources`.
For `update` or `unchanged`, include `existing_ref` in `coverage.read_cases`.

| Action | Allowed status |
|---|---|
| `create`, `update` | `draft`, `blocked`, `preview` |
| `unchanged`, `none` | `unchanged` |

Changed cases include `preconditions`, `variants`, and `steps` with `action` and `expected`.
For a draft, include `estimate.seconds` as a positive integer and `estimate.basis`.

`verification` contains:
- `basis`: `new_run`, `existing_report`, `mixed`, `none`;
- `new_run`: true for `new_run` or `mixed`, otherwise false;
- `result`: `passed`, `failed`, `partial`, `not_run`;
- `environment`, `version`, `checked_at`, `scope`;
- `covered_steps`: tested step numbers, starting at 1;
- `artifacts`: local evidence paths; `limitations`: unresolved issues within the target path.

A draft needs a passed check of every step, an execution report, no unresolved limitations, and available coverage.
A blocked case needs an explanation. Early previews remain untested.
Record variants and mock limits in `scope`. Include execution evidence beyond screenshots.

`media` has `required`, `reason`, `items`.
Each item has `path`, `role`, `caption`, `step` (0 for initial conditions), and `viewed: true` after visual examination.
A draft needs all required media.

Each draft needs `automation`: `checked`, `found`, `gaps`, `action`, `target`, `reason`.
Each found test has `ref` and `covers`. See [automation](automation.md) for actions.
Unknown or inaccessible repositories need `action: blocked`.

For an external write, include `external.system`, `case_ref`, `state`, `readback`, and `checked`.
Use saved response paths for `readback`.
For `state: verified`, examine `draft`, `content`, `estimate`, `source_links`, and `media`.
An unconfirmed write needs case status `blocked`.

## Files and report

List outstanding work in top-level `not_done`.
Use evidence paths relative to the result directory. Files must exist and contain data.
Do not use generated cases, `result.json`, or `report.md` as execution evidence.

Run `scripts/finalize_cases.py <result-dir>/result.json` from the loaded skill directory.
It examines the contract and writes `cases/<id>.md` and `report.md`.
Read the output. After failure, any previous report is stale.
The helper examines structure and files; the agent examines facts.
