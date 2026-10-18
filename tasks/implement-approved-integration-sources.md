# Implement the approved integration source files

**Decision:** [Skill-led integration design](../decisions/20261018-2243-skill-led-integration-design.md).

This is a reviewed task record only. Its creation does not authorize execution.

## What

Create these three source files, with paths relative to
`/home/madkroll/thinkforward-ai/`:

1. `agent-hub/skills/install-integration/SKILL.md`.
2. `agent-hub/skills/install-integration/scripts/bootstrap.sh`.
3. `integrations/skills/hello-world/SKILL.md`.

Do not install the skills or tools, change Agent Hub home, configure aliases,
create project capability mappings, or execute an integration.

## Why

Implement the approved two-skill design and reusable bootstrap while keeping
source implementation separate from deployment, installation approval, and
user-run verification.

## How

1. Follow each repository's applicable instructions. If a destination has
   appeared or changed since review, inspect it and preserve unrelated work.
2. Use the two approved skill texts from the linked decision verbatim,
   including metadata, resource paths, and the shared approval gate.
3. Implement a sourceable Bash bootstrap at the shared skill's declared
   resource path. It must:
   1. Resolve Hub home from `AGENT_HUB_HOME`, defaulting to `$HOME/.agent-hub`.
   2. Add Hub's existing `bin/` directory to PATH when present, without
      duplication when sourced repeatedly.
   3. Enable Bash alias expansion.
   4. Source Hub's `aliases.sh` when present and tolerate its absence.
   5. Perform no installation, file writes, or tool verification.
4. Preserve the existing hello-world program and development tests.
   Do not add an alias helper, command wrappers, installed-tool inventory,
   or empty default alias configuration.
5. Validate the new source documents and Bash syntax. Check bootstrap behavior
   in isolated fixture shells, using temporary Hub homes rather than the
   user's installed Hub. Inspect alias definitions without invoking them;
   do not execute any integration as a test.
6. Report created source files and validation results. Do not deploy, activate
   the user's runtime, edit shell startup files, commit, push, or install.

## Acceptance criteria

1. All three source files exist at the specified locations. Both skill texts
   match the accepted decision.
2. Metadata resource references resolve within their respective skill
   directories; the hello-world dependency and resource arrays are retained.
3. Bash syntax checks pass. Isolated bootstrap checks cover default and
   overridden Hub homes, present and absent bin/alias files, repeat sourcing
   without duplicate PATH entries, alias expansion, and loaded alias definitions.
4. Validation creates no files in fixture Hub homes as a side effect of
   sourcing bootstrap and invokes no integration commands.
5. Existing source content and installed Hub content remain unchanged.
   No global skill installation, alias selection, project mapping, or
   automatic functional verification occurs.

## Prerequisites

1. The approved design and exact skill texts linked above are available.
2. Both source repositories are available under
   `/home/madkroll/thinkforward-ai/`.
3. The existing hello-world resource is
   `integrations/skills/hello-world/scripts/hello-world.sh`.
4. Execution requires a separate explicit user request; only creation of this
   task record is currently authorized.

## Dependencies

None.
