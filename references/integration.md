# Optional TMS output

Use an available official client and its current schema.
Resolve the project through [project context](project-context.md). A project choice does not authorize a write.
Read required fields, draft statuses, shared conditions, attachment operations, links, and time units.
Convert local seconds to the target units.

Perform only authorized draft changes. Preserve valid content when an API replaces whole arrays.
Read the target before an update. Resolve concurrent changes before writing.
Do not repeat a timed-out create request until you establish its outcome.
An ambiguous identifier or failed read-back leaves the write unconfirmed.

After each write, independently read the case, links, and attachments.
Examine the project, identifier, draft status, full content, time estimate, source links, and required media.
Examine link types. Prevent duplicate links.
Save the responses. Record the checks and the actual case link in the report.
Report a successful write only after these checks. Otherwise, mark the write unconfirmed and the case blocked.

Create project settings, publish comments, archive cases, or delete data only within separate authorization.
For external previews, follow the available system contract and the user's explicit request.
A saved preview does not prove execution.
