installation skill must guide user until integration is fully installed and works

Approved wording for `install-integration`:

description: Discover or install integrations, configure optional shell aliases, guide the user until the integration works, and map project capabilities.

10. Guide the user until the integration is fully installed and works. Give one remaining user-run step at a time, such as privileged dependency installation, activation, or verification, with its expected result, and wait for the outcome. Do not automatically run the installed tool, its aliases, smoke tests, or self-tests. On failure, diagnose with read-only inspection and propose the next step; changes beyond the approved plan need a new preview and approval. Finish when the user confirms it works; if they stop earlier, report readiness as unverified.
